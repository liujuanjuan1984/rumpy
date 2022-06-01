# settings.py
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(verbose=True, override=True)

import os

QUORUM_PORT = os.getenv("QUORUM_PORT")
print(QUORUM_PORT)

QUORUM_PORT = 123456
print(QUORUM_PORT)
print(os.getenv("QUORUM_PORT"))
