from flask import Blueprint, jsonify, request, g
import json


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/teams', methods=['GET'])
def list_of_rooms():
    return jsonify([{'room': 'test'}])


@api.route('/teams/<team_name>/', methods=['GET'])
def get_room_info(team_name):
    team_info = g.redis.get(team_name)
    if team_info is None:
        return jsonify({'error': 'No team found for {}'.format(team_name)})
    return jsonify(json.loads(team_info))


@api.route('/teams/<team_name>/members', methods=['GET'])
def get_team_members(team_name):
    team_info = get_team_data(team_name)
    if team_info is None:
        return jsonify({'error': 'No team found for {}'.format(team_name)})
    return jsonify(team_info['members'])


@api.route('/teams/<team_name>/members/admins', methods=['GET'])
def get_team_admin(team_name):
    team_info = get_team_data(team_name)
    if team_info is None:
        return jsonify({'error': 'No team found for {}'.format(team_name)})
    privileged_members = []
    for member in team_info['members']:
        member_role = member["role"]
        if member_role == "owner" or member_role == "admin":
            privileged_members.append(member)
    return jsonify(privileged_members)


@api.route('/teams/<team_name>/history', methods=['GET'])
def get_room_chat_history(team_name):
    team_info = get_team_data(team_name)
    if team_info is None:
        return jsonify({'error': 'No team found for {}'.format(team_name)})
    return jsonify(team_info['messages'])


def get_team_data(team_name):
    team_info = g.redis.get(team_name)
    if team_info is None:
        return None
    return json.loads(team_info)


def add_message(team_name, message):
    team_info = get_team_data(team_name)
    team_info["messages"].append(message)
    g.redis.set(team_name, json.dumps(team_info))


def create_team(team_data):
    team_name = team_data['channel']
    team_data['members'] = [{"username": team_data['username'], "role": "owner"}]
    team_data['messages'] = []
    g.redis.set(team_name, json.dumps(team_data))


def user_exists_team(team_data, username):
    for member in team_data['members']:
        if member["username"] == username:
            return True
    return False


def join_team(team_data, username):
    team_name = team_data['channel']
    if user_exists_team(team_data, username) is False:
        team_user = {"username": username, "role": "user"}
        team_data['members'].append(team_user)
        g.redis.set(team_name, json.dumps(team_data))


