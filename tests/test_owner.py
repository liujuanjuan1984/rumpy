import pytest
from rumpyconfig import RumpyConfig
from rumpy import RumClient

client = RumClient(**RumpyConfig.GUI)


def test_owner():
    for gid in client.node.groups_id:
        if client.group.is_owner(gid):
            print(gid, client.group.info(gid).group_name)


if __name__ == "__main__":
    test_owner()
