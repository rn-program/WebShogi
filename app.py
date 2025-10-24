from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os
import shogi

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("game.html")


# game.htmlから得た着手が合法手かの判定
@socketio.on("get_move")
def judge_move(data):
    board = shogi.Board()
    move = data.get("move")
    board_sfen = data.get("board_sfen")
    board.set_sfen(board_sfen)
    legal_moves_list = [m.usi() for m in board.legal_moves]

    # 合法手の場合の分岐
    # => 対戦相手との盤共有
    if move in legal_moves_list:
        board.push(shogi.Move.from_usi(move))
        new_sfen = board.sfen()
        emit("update_board", {"board_sfen": new_sfen})
    else:
        emit("illegal_move", {"msg": f"反則手です: {move}"})


# 成りを検知した時の反則判定
@socketio.on("judge_promote")
def judge_promote(data):
    room_number = data.get("room_number")
    board = shogi.Board()
    move = data.get("move")
    board_sfen = data.get("board_sfen")

    board.set_sfen(board_sfen)
    legal_moves_list = [m.usi() for m in board.legal_moves]

    if move in legal_moves_list:
        emit("legal_move", room=room_number)
    else:
        emit("illegal_move", {"msg": f"反則手です: {move}"}, room=room_number)

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)