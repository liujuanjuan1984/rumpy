import base64

from tests import client


def test_fileinfo(content_str_bytes=None):
    """把加密过的 json 数据文本，转换回可读的 json 数据。"""

    csb = (
        content_str_bytes
        or "eyJtZWRpYVR5cGUiOiJhcHBsaWNhdGlvbi9lcHViK3ppcCIsIm5hbWUiOiLkuI7mnLrlmajotZvot5EgLSDkuJzopb/mloflupMuZXB1YiIsInRpdGxlIjoi5LiO5py65Zmo6LWb6LeRIiwic2hhMjU2IjoiNjJhZDY3YzVmNjc1YTgxYzRjYjZkYzUzYjY0ODBjYTY3YzcwYmM1ZDBiZDY4MDA3YjY4NmY2OGQwMzdjYzkzOCIsInNlZ21lbnRzIjpbeyJpZCI6InNlZy0xIiwic2hhMjU2IjoiNWZkYzQ4MTM5ZTM3NjQyOWU1OTRiZWI1NDhiZjlmZWZiNjYyOTZjMmY1ZDE2ZmQxMDY3YzE4MDhiOTQwZGFmOSJ9LHsiaWQiOiJzZWctMiIsInNoYTI1NiI6ImU2YTQ5NjVlNzMwODRjOTliNjRlOTU0Njc5YzYyZjM5MDU5YzU3OTFkYWFlNDNmMDg4MjE0NDZiOWU4ZjdkMWMifV19"
    )

    return eval(base64.b64decode(csb).decode("utf-8"))


if __name__ == "__main__":
    print(test_fileinfo())
