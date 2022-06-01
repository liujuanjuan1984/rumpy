from flask import Flask

from rumpy import LightNode

app = Flask(__name__)

app = LightNode(port=6002).init_app(app)


@app.route("/")
def get_groups():
    gids = app.rum.api.list_groups()
    return f"<p> Node in these groups: {gids}</p>"


if __name__ == "__main__":
    app.run(debug=True)
