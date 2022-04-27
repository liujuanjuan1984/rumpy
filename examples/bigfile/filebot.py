from rumpy import RumClient
import os
import math
import hashlib
import base64
import json

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
            "mediaType": "application/epub+zip",
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
            raise ValueError(f"{file_path} is not a file.")

        if not file_path.endswith(".epub"):
            raise ValueError(f"{file_path} is not a .epub file.")

        for obj in self._file_to_objs(file_path):
            self.group._send(obj)
