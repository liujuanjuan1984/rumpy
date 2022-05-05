"""
Mixin Bot API for Python 3.x
This SDK base on 'https://github.com/learnforpractice/mixin-python/blob/main/pysrc/mixin_bot_api.py'
"""
import base64
import datetime
import httpx
import hashlib
import jwt
import json
import uuid
from typing import Union, List
from cryptography.hazmat.primitives.asymmetric import ed25519


class MixinBotApi:
    def __init__(self, mixin_config):

        self.client_id = mixin_config["client_id"]
        self.pay_session_id = mixin_config["session_id"]
        self.pay_pin = mixin_config["pin"]
        self.pin_token = mixin_config["pin_token"]
        self.private_key = mixin_config["private_key"]
        self.private_key_base64 = self.private_key

        if self.private_key.find("RSA PRIVATE KEY") >= 0:
            self.algorithm = "RS512"
        else:
            self.algorithm = "EdDSA"
            self.private_key = self.decode_ed25519(self.private_key)

        self.client = httpx.AsyncClient(timeout=None)  # timeout=None is for error:httpx.ReadTimeout
        self.api_base_url = "https://api.mixin.one"

    async def close(self):
        await self.client.aclose()

    def genPOSTSig(self, uristring, bodystring):
        return self.gen_get_post_sig("POST", uristring, bodystring)

    def generate_sig(self, method, uri, body):
        hashresult = hashlib.sha256((method + uri + body).encode("utf-8")).hexdigest()
        return hashresult

    def gen_get_post_sig(self, methodstring, uristring, bodystring):
        jwtSig = self.generate_sig(methodstring, uristring, bodystring)
        return jwtSig

    def decode_ed25519(cls, priv):
        if not len(priv) % 4 == 0:
            priv = priv + "===="
        priv = base64.urlsafe_b64decode(priv)
        return ed25519.Ed25519PrivateKey.from_private_bytes(priv[:32])

    def gen_post_jwt_token(self, uristring, bodystring, jti):
        jwtSig = self.genPOSTSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode(
            {"uid": self.client_id, "sid": self.pay_session_id, "iat": iat, "exp": exp, "jti": jti, "sig": jwtSig},
            self.private_key,
            algorithm=self.algorithm,
        )
        return encoded

    def __genUrl(self, path):
        """
        generate API url
        """
        return self.api_base_url + path

    async def __genNetworkPostRequest(self, path, body, auth_token=""):

        """
        generate Mixin Network POST http request
        """
        # transfer obj => json string
        if isinstance(body, (dict, list)):
            body = json.dumps(body)
        # generate robot's auth token
        if auth_token == "":
            auth_token = self.gen_post_jwt_token(path, body, str(uuid.uuid4()))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + auth_token,
            "X-Request-Id": str(uuid.uuid4()),
        }
        # generate url
        url = self.__genUrl(path)

        r = await self.client.post(url, data=body, headers=headers)

        r = r.json()
        if "error" in r:
            raise Exception(r["error"])
        return r["data"]

    async def post(self, path, body, auth_token=""):
        return await self.__genNetworkPostRequest(path, body, auth_token)

    async def send_message(self, conversation_id: str, category: str, data: str):
        if isinstance(data, str):
            data = data.encode()
        msg = {
            "conversation_id": conversation_id,
            "message_id": str(uuid.uuid4()),
            "category": category,
            "data": base64.b64encode(data).decode(),
        }
        return await self.post("/messages", msg)

    async def send_text_message(self, conversation_id: str, data: Union[str, bytes]):
        return await self.send_message(conversation_id, "PLAIN_TEXT", data)

    async def send_img_message(self, conversation_id: str, data: str):

        msg = {
            "conversation_id": conversation_id,
            "message_id": str(uuid.uuid4()),
            "category": "PLAIN_IMAGE",
            "data": data,
        }
        return await self.post("/messages", msg)
