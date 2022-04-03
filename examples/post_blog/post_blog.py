import time
import os
import sys
from officepy import JsonFile, Dir, File
from rumpy import RumClient


def main():
    # init
    client = RumClient()

    # create a group
    seed = client.group.create("mytest_postblog", app_key="group_post")
    client.group_id = seed["group_id"]

    # get the articles file for test
    test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
    article_files = Dir(test_data_dir).search_files_by_types((".md", ".txt"))

    # post to rum
    failed = []
    for ifile in article_files:
        ilines = File(ifile).readlines()
        # split tile and content.
        for line in ilines:
            if line.startswith("# "):
                title = line.replace("# ", "").replace("\n", "")
                n = ilines.index(line)
                break
        content = "".join(ilines[n + 1 :])

        relay = {"content": content, "name": title}
        resp = client.group.send_note(**relay)

        if "trx_id" not in resp:
            failed.append(ifile)
        else:
            print("success:", ifile)

        time.sleep(1)

    print("failed:", failed or "None")


if __name__ == "__main__":
    main()
