from flask import Flask

from rumpy import LightNode

app = Flask(__name__)

app = LightNode().init_app(app)


@app.route("/")
def get_groups():
    gids = app.rum.api.groups()
    return f"<p> Node in these groups: {gids}</p>"


if __name__ == "__main__":
    app.run(debug=True)
