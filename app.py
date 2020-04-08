from flask import Flask, render_template, g
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from flask_cors import CORS

from database import connect_redis
from api import api, add_message, get_team_data, create_team, join_team

import logging
import json
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

app = Flask(__name__)
app.register_blueprint(api)

app.config['SECRET_KEY'] = 'totallySecret'

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


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

@socketio.on('signal')
def handle_signal(data):
    connect_redis()
    print('Signal')
    if (data['type'] == 'access_requested'):
        # TODO: check if token is valid
        print('--------')
        emit('signal', {'type': 'access_granted'}, room=data['channel'])
    else:
        print('--------')
        emit('signal', data, room=data['channel'])


@socketio.on('join')
def join_chat(data):
    connect_redis()
    team_name = data['channel']
    team = get_team_data(team_name)
    username = data['username']
    if team is None:
        create_team(data)
    else:
        join_team(team, username)
    join_room(team_name)
    send({'content': username + ' has entered the room.'}, room=team_name)


@socketio.on('leave')
def leave_chat(data):
    username = data['username']
    room = data['channel']
    leave_room(room)
    send(username + ' has left the room.', room=room)


if __name__ == '__main__':
    socketio.run(app, debug=True)
