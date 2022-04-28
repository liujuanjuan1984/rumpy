from rumpy import RumClient
import os
import math
import hashlib
import base64
import json
import filetype

CHUNK_SIZE = 150 * 1024  # 150kb


class FileBot(RumClient):
    def init(self, group_id=None, group_name=None):
        self.group_id = (
            group_id or self.group.create(group_name=group_name or "mytest_epub", app_key="group_epub")["group_id"]
        )

    def _fileinfo_obj(self, file_info):
        content = base64.b64encode(json.dumps(file_info).encode()).decode("utf-8")
        return {
            "type": "File",
            "name": "fileinfo",
            "file": {"compression": 0, "mediaType": "application/json", "content": content},
        }

    def _file_seg_obj(self, num, ibytes):
        content = base64.b64encode(ibytes).decode("utf-8")
        return {
            "type": "File",
            "name": f"seg-{num}",
            "file": {"compression": 0, "mediaType": "application/octet-stream", "content": content},
        }

    def _sha256(self, ibytes):
        return hashlib.sha256(ibytes).hexdigest()

    def _file_to_objs(self, file_path):

        file_total_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path).encode().decode("utf-8")
        file_obj = open(file_path, "rb")
        fileinfo = {
            "mediaType": filetype.guess(file_path).mime,
            "name": file_name,
            "title": file_name.split(".")[0],
            "sha256": self._sha256(file_obj.read()),
            "segments": [],
        }

        chunks = math.ceil(file_total_size / CHUNK_SIZE)
        objs = []

        for i in range(chunks):
            if i + 1 == chunks:
                current_size = file_total_size % CHUNK_SIZE
            else:
                current_size = CHUNK_SIZE
            file_obj.seek(i * CHUNK_SIZE)
            ibytes = file_obj.read(current_size)
            fileinfo["segments"].append({"id": f"seg-{i+1}", "sha256": self._sha256(ibytes)})
            objs.append(self._file_seg_obj(i + 1, ibytes))

        objs.insert(0, self._fileinfo_obj(fileinfo))
        file_obj.close()
        return objs

    def upload(self, file_path):
        if not os.path.isfile(file_path):
            return print(f"{file_path} is not a file.")
        for obj in self._file_to_objs(file_path):
            self.group._send(obj)

    def _file_infos(self):
        trxs = self.group.all_content_trxs()
        infos = []
        filetrxs = []
        for trx in trxs:
            if trx["Content"]["name"] == "fileinfo":
                info = eval(base64.b64decode(trx["Content"]["file"]["content"]).decode("utf-8"))
                print(info)
                infos.append(info)
            if trx["Content"].get("type") == "File":
                filetrxs.append(trx)
        return infos, filetrxs

    def _down_load(self, file_dir, info, trxs):

        ifilepath = os.path.join(file_dir, info["name"])
        if os.path.exists(ifilepath):
            return print(ifilepath, "file exists.")

        # _check_trxs
        right_shas = [i["sha256"] for i in info["segments"]]
        contents = {}

        for trx in trxs:
            content = base64.b64decode(trx["Content"]["file"]["content"])
            csha = hashlib.sha256(content).hexdigest()
            if csha in right_shas:
                contents[csha] = trx

        flag = True

        for seg in info["segments"]:
            if seg["sha256"] not in contents:
                print(seg, "trx is not exists...")
                flag = False
                break
            if contents[seg["sha256"]]["Content"].get("name") != seg["id"]:
                print(seg, "name is different...")
                flag = False
                break

        if flag:
            ifile = open(ifilepath, "wb+")
            for seg in info["segments"]:
                content = base64.b64decode(contents[seg["sha256"]]["Content"]["file"]["content"])
                ifile.write(content)
            ifile.close()
            print(ifilepath, "downloaded!")

    def download(self, file_dir):
        infos, trxs = self._file_infos()
        for info in infos:
            self._down_load(file_dir, info, trxs)
