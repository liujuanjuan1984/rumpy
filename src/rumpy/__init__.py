import logging
from .client import RumClient
from .client.module import *

__version__ = "0.0.5"
__author__ = "liujuanjuan1984"

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
