import logging
from rumpy.client import RumClient
from rumpy.client.module import *

__version__ = "0.1.5"
__author__ = "liujuanjuan1984"

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())