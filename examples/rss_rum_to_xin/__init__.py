import datetime
import logging


# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(
    format="%(name)s %(asctime)s %(levelname)s %(message)s",
    filename=f"rss_bot_{datetime.date.today()}.log",
    level=logging.DEBUG,
)
