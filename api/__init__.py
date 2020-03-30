from flask import Blueprint, jsonify, request, g
import json


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/rooms', methods=['GET'])
def list_of_rooms():
    return jsonify([{'room': 'test'}])


@api.route('/rooms/create', methods=['POST'])
def create_room():
    room_data = request.get_json()
    room_name = room_data['name']
    room_data['members'] = []
    room_data['messages'] = []
    room_info = get_room_info(room_name)
    if room_info is not None:
        return jsonify({'error': '{} room already exists'.format(room_name)})
    g.redis.set(room_name, json.dumps(room_data))
    return room_data


@api.route('/rooms/<room_name>/join', methods=['POST'])
def join_room(room_name):
    request_data = request.get_json() #todo with user tokens
    room_info = get_room_info(room_name)
    member = {"name": request_data['name']}
    room_info["members"].append(member)
    g.redis.set(room_name, json.dumps(room_info))
    return jsonify(room_info)


@api.route('/rooms/<room_name>/', methods=['GET'])
def get_room_info(room_name):
    room_info = g.redis.get(room_name)
    if room_info is None:
        return jsonify({'error': 'No room found for {}'.format(room_name)})
    return jsonify(json.loads(room_info))


@api.route('/rooms/<room_name>/members', methods=['GET'])
def get_room_members(room_name):
    room_info = get_room_info(room_name)
    return jsonify(room_info['members'])


@api.route('/rooms/<room_name>/history', methods=['GET'])
def get_room_chat_history(room_name):
    room_info = get_room_info(room_name)
    return jsonify(room_info['messages'])


def get_room_info(room_name):
    room_info = g.redis.get(room_name)
    return json.loads(room_info)


def add_message(room_name, message):
    room_info = get_room_info(room_name)
    room_info["messages"].append(message)
    g.redis.set(room_name, json.dumps(room_info))

