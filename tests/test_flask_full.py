from flask import Flask

from rumpy import FullNode

app = Flask(__name__)

app = FullNode(port=62663).init_app(app)


@app.route("/")
def get_groups():
    gids = app.rum.api.groups_id
    return f"<p> Node in these groups: {gids}</p>"


if __name__ == "__main__":
    app.run(debug=True)
