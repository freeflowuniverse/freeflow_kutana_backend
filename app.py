from flask import Flask, Response, request, json, redirect
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from flask_cors import CORS

from database import connect_redis
from config.freeflow_config import SOCKET_SECRET
from api import api_blueprint, add_message, get_team_data, create_team, join_team, is_3bot_user

import logging
import json
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

app = Flask(__name__)
app.register_blueprint(api_blueprint)

app.config['SECRET_KEY'] = "SOCKET_SECRET"

CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
socketio = SocketIO(app, cors_allowed_origins="*")

roomsSharingScreen = {}

@socketio.on('connect')
def connect_socket():
    print("Client connected")

@socketio.on('disconnect')
def disconnect_socket():
    print('Client disconnected')
    
    referrer = request.referrer

    # Yeah, yeah I know, bite me.
    if referrer[-1] == "/":
        referrer = referrer[:-1]

    # Figure out a better way to pass this data then the referrer.
    channel = referrer.split("/").pop()
    socket_id = request.sid

    if channel in roomsSharingScreen:
        if roomsSharingScreen[channel]["socket_id"] == socket_id:
            print("User that was sharing has disconnected, stopping the share ... ")
            tmp = roomsSharingScreen[channel]
            del roomsSharingScreen[channel]
            tmp["type"] = "screenshare_stopped"
            print(tmp)
            emit('signal', tmp, room=channel)
            roomsSharingScreen[channel] = {}
            

@socketio.on('message')
def handle_message(data):
    connect_redis()
    emit('message', data, room=data['channel'].lower())
    add_message(data['channel'].lower(), data)

@socketio.on('signal')
def handle_signal(data):
    connect_redis()

    print('Signal')
    if (data['type'] == 'access_requested'):
        emit('signal', {'type': 'access_granted'})
    elif (data['type'] == 'screenshare_started'):
        print("Started screenshare with SID")
        print(request.sid)
        data.update({'socket_id': request.sid})
        roomsSharingScreen[data['channel'].lower()] = data
        emit('signal', data, room=data['channel'].lower())
    elif (data['type'] == 'screenshare_stopped'):
        del roomsSharingScreen[data['channel'].lower()]
        emit('signal', data, room=data['channel'].lower())
    else:
        emit('signal', data, room=data['channel'].lower())

@socketio.on('join')
def join_chat(data):
    connect_redis()
    team_name = data['channel'].lower()
    if team_name == 'kimeru':
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@ NOTIFY SIGNAGE!!")
    team = get_team_data(team_name)
    username = data['username']
    if team is None:
        create_team(data)
    else:
        join_team(team, username)
    join_room(team_name)
    if team_name in roomsSharingScreen:
        emit('signal', roomsSharingScreen[team_name])
    content = {'content': username + ' has entered the room.'}
    add_message(team_name, content)
    emit(content, room=team_name)

@socketio.on('leave')
def leave_chat(data):
    username = data['username']
    room = data['channel'].lower()
    team_name = data['channel'].lower()
    content = {'content': username + ' has left the room.'}
    add_message(team_name, content)
    emit(content, room=team_name)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
