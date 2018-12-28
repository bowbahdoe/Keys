"""Flask server for keys"""
import flask
from simplified_game import SimplifiedKeysGame
from board import Board

app = flask.Flask(__name__)

game = SimplifiedKeysGame()

@app.route("/move", methods=["POST"])
def move():
    json = flask.request.get_json()
    try:
        game.move(json["team"], tuple(json["from"]), tuple(json["to"]))
        return flask.jsonify(game.summarize())
    except ValueError e:
        return flask.jsonify({"error": "Invalid value types passed"})
@app.route("/state", methods=["GET"])
def state():
    return flask.jsonify(game.summarize())

if __name__ == "__main__":
    app.run()
