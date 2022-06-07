import logging

logger = logging.getLogger(__name__)


def _init_app(_client, flask_app, rum_kspasswd=123456, rum_port=62663):
    """for flask extensions"""
    if not hasattr(flask_app, "extensions"):
        flask_app.extensions = {}
    flask_app.extensions["rum"] = _client

    flask_app.config.setdefault("RUM_KSPASSWD", rum_kspasswd)
    flask_app.config.setdefault("RUM_PORT", rum_port)
    flask_app.rum = _client
    return flask_app
