import logging
import os

logger = logging.getLogger(__name__)


def _init_app(_client, flask_app, rum_kspasswd=None, rum_port=None):
    """for flask extensions"""
    if not hasattr(flask_app, "extensions"):
        flask_app.extensions = {}
    flask_app.extensions["rum"] = _client

    rum_kspasswd = rum_kspasswd or os.getenv("RUM_KSPASSWD")
    rum_port = rum_port or os.getenv("RUM_PORT")

    flask_app.config.setdefault("RUM_KSPASSWD", rum_kspasswd)
    flask_app.config.setdefault("RUM_PORT", rum_port)
    flask_app.rum = _client
    return flask_app
