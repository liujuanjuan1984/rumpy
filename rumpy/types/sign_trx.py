import base64
import hashlib
import json
import os
import time
import uuid
from typing import Any, Dict

import eth_keys
import requests
from Crypto.Cipher import AES
from google.protobuf import any_pb2, json_format

from rumpy.exceptions import *
from rumpy.types import quorum_pb2 as pbQuorum

nonce = 1


def aes_encrypt(key: bytes, data: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_GCM, nonce=os.urandom(12))
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return b"".join([cipher.nonce, ciphertext, tag])


def aes_decrypt(key: bytes, data: bytes) -> bytes:
    nonce, tag = data[:12], data[-16:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(data[12:-16], tag)


def get_sender_pub_key(private_key: bytes) -> str:
    pk = eth_keys.keys.PrivateKey(private_key)
    return base64.urlsafe_b64encode(pk.public_key.to_compressed_bytes()).decode()


def check_timestamp(timestamp):
    if timestamp is None:
        return int(time.time() * 1e9)
    try:
        ts = str(timestamp).replace(".", "")
        if len(ts) > 19:
            ts = ts[:19]
        elif len(ts) < 19:
            ts += "0" * (19 - len(ts))
        ts = int(ts)
        return ts
    except Exception as e:
        print(e)
        return int(time.time() * 1e9)


def trx_encrypt(
    group_id: str,
    aes_key: bytes,
    private_key: bytes,
    obj: Dict[str, Any],
    timestamp=None,
) -> Dict[str, str]:
    obj_pb = pbQuorum.Object(**obj)
    any_obj_pb = any_pb2.Any()
    any_obj_pb.Pack(obj_pb, type_url_prefix="type.googleapis.com/")
    data = any_obj_pb.SerializeToString()
    encrypted = aes_encrypt(aes_key, data)

    priv = eth_keys.keys.PrivateKey(private_key)
    sender_pub_key = get_sender_pub_key(private_key)

    timestamp = check_timestamp(timestamp)

    now = time.time()
    global nonce
    trx = {
        "TrxId": str(uuid.uuid4()),
        "GroupId": group_id,
        "Data": encrypted,
        "TimeStamp": timestamp,
        "Version": "1.0.0",
        "Expired": timestamp + int(30 * 1e9),
        "Nonce": nonce + 1,
        "SenderPubkey": sender_pub_key,
    }

    trx_without_sign_pb = pbQuorum.Trx(**trx)
    trx_without_sign_pb_bytes = trx_without_sign_pb.SerializeToString()
    hash = hashlib.sha256(trx_without_sign_pb_bytes).digest()
    signature = priv.sign_msg_hash(hash).to_bytes()
    trx["SenderSign"] = signature

    trx_pb = pbQuorum.Trx(**trx)
    trx_json_str = json.dumps(
        {
            "TrxBytes": base64.b64encode(trx_pb.SerializeToString()).decode(),
            # "JwtToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        }
    )

    enc_trx_json = aes_encrypt(aes_key, trx_json_str.encode())

    send_trx_obj = {
        "GroupId": group_id,
        "TrxItem": base64.b64encode(enc_trx_json).decode(),
    }
    return send_trx_obj


def trx_decrypt(aes_key: bytes, encrypted_trx: dict):
    """
    encrypted_trx :
    {'TrxId': 'e99cca77-f31f-40ea-9677-8b0679755130', 'Type': 'POST', 'GroupId': '2e39139f-a48a-4a3c-8463-d85a28e29674', 'Data': 'B2TfJUm2BqP+JB5n4bYgcLvNfv4h5Lq02auhVRuDiYzshvKtYCGAprZLg3uSeH29U3hVs/Fskn5e9tyDggNvwVCcwf1RPghKawjd9lohL0RxGZDAPb9Kzhamlg6u6x/pSAguGKk6WO0IKjjOsBfAndk/nv0EqDitIlO/o9xW', 'TimeStamp': '1658931141167696896', 'Version': '1.0.0', 'Expired': '1658931171167696896', 'ResendCount': '0', 'Nonce': '2', 'SenderPubkey': 'Ay-MErjDWlc04j464s7Y3IOVmjKqM3FwD1_Dzl7XhjGq', 'SenderSign': 'eAW8HGVVPi/vUGWn5r/kmMi7014+pJ2dSg9P/CltdVZD7V6z5crrO25xxXMczjITcPjuIKBsQFUmQvPtbFR0ewA=', 'StorageType': 'CHAIN'}

    decrpyted_trx :
    {'TrxId': 'e99cca77-f31f-40ea-9677-8b0679755130', 'Publisher': 'Ay-MErjDWlc04j464s7Y3IOVmjKqM3FwD1_Dzl7XhjGq', 'Content': {'type': 'Note', 'content': '你好，测试新版本2022-07-27 22:12:21.143760'}, 'TypeUrl': 'quorum.pb.Object', 'TimeStamp': 1658931141167696896}

    """
    data = encrypted_trx.get("Data")
    if data is None:
        raise ParamValueError("Data is None")
    data = base64.b64decode(data)
    data = aes_decrypt(aes_key, data)
    any_obj = any_pb2.Any().FromString(data)
    obj = pbQuorum.Object()
    any_obj.Unpack(obj)
    dict_obj = json_format.MessageToDict(obj)
    decrpyted_trx = {
        "TrxId": encrypted_trx.get("TrxId"),
        "Publisher": encrypted_trx.get("SenderPubkey"),
        "Content": dict_obj,
        "TypeUrl": "quorum.pb.Object",
        "TimeStamp": encrypted_trx.get("TimeStamp"),
    }
    return decrpyted_trx
