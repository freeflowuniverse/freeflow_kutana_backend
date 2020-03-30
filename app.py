from flask import Flask, render_template, g
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from flask_cors import CORS

from database import connect_redis
from api import api, add_message, get_room_info

import logging
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

app = Flask(__name__)
app.register_blueprint(api)

app.config['SECRET_KEY'] = 'totallySecret'

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return render_template('socket.html')


@app.before_request
def before_request():
    connect_redis()


@socketio.on('connect')
def connect_socket():
    print("Client connected")


@socketio.on('disconnect')
def disconnect_socket():
    print('Client disconnected')


@socketio.on('message')
def handle_message(data):
    connect_redis()
    emit('message', data, room=data['channel'])
    add_message(data['channel'], data)


@socketio.on('join')
def join_chat(data):
    connect_redis()
    room = get_room_info(data['room'])
    if room is None:
        send(data['room'] + ' room does not exists.')
        return
    username = data['username']
    join_room(room)
    send(username + ' has entered the room.', room=room['name'])


@socketio.on('leave')
def leave_chat(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)


if __name__ == '__main__':
    socketio.run(app, debug=True)
