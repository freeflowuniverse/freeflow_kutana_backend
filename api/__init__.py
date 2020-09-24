from flask import Blueprint, jsonify, g, request
from database import connect_redis
from config.freeflow_config import THREE_BOT_CONNECT_URL
from flask_cors import CORS

import nacl
import nacl.signing
import nacl.encoding
from urllib.request import urlopen
import base64

import json

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

CORS(api_blueprint)

@api_blueprint.before_request
def before_request():
    connect_redis()

""" @api_blueprint.before_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response """

@api_blueprint.route('/teams/<team_name>/', methods=['GET'])
def get_room_info(team_name):
    team_info = g.redis.get(team_name)
    if team_info is None:
        return jsonify({'error': 'No team found for {}'.format(team_name)}), 404
    return jsonify(json.loads(team_info))


@api_blueprint.route('/teams/<team_name>/members', methods=['GET'])
def get_team_members(team_name):
    team_info = get_team_data(team_name)
    if team_info is None:
        return jsonify({'error': 'No team found for {}'.format(team_name)}), 404
    return jsonify(team_info['members'])


@api_blueprint.route('/teams/<team_name>/members/admins', methods=['GET'])
def get_team_admin(team_name):
    team_info = get_team_data(team_name)
    if team_info is None:
        return jsonify({'error': 'No team found for {}'.format(team_name)}), 404
    privileged_members = []
    for member in team_info['members']:
        member_role = member["role"]
        if member_role == "owner" or member_role == "admin":
            privileged_members.append(member)
    return jsonify(privileged_members)


@api_blueprint.route('/teams/<team_name>/history', methods=['GET'])
def get_room_chat_history(team_name):
    team_info = get_team_data(team_name)
    if team_info is None:
        return jsonify({'error': 'No team found for {}'.format(team_name)}), 404
    return jsonify(team_info['messages'][-200:])


@api_blueprint.route('/teams/<team_name>/invite', methods=['POST'])
def save_invite_url(team_name):
    body_data = request.json
    team_info = get_team_data(team_name)
    if team_info is None:
        return jsonify({'error': 'No team found for {}'.format(team_name)}), 404
    if 'invites' not in team_info:
        team_info['invites'] = [{'token': body_data['token'], 'time_active': None, 'times_used': 0}]
        save_team_info(team_name, team_info)
        return jsonify(team_info['invites'])
    invite_object = {'token': body_data['token'], 'time_active': None, 'times_used': 0}
    team_info['invites'].append(invite_object)
    save_team_info(team_name, team_info)
    return jsonify(invite_object)


def get_team_data(team_name):
    team_info = g.redis.get(team_name)
    if team_info is None:
        return None
    return json.loads(team_info)


def add_message(team_name, message):
    team_info = get_team_data(team_name)
    if team_info is None:
        return jsonify({'error': 'No team found for {}'.format(team_name)}), 404
    team_info["messages"].append(message)
    save_team_info(team_name, team_info)


def create_team(team_data):
    team_name = team_data['channel']
    team_data['members'] = [{"username": team_data['username'], "role": "owner"}]
    team_data['messages'] = []
    team_data['invites'] = []
    save_team_info(team_name, team_data)


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
        save_team_info(team_name, team_data)


def save_team_info(team_name, team_info):
    g.redis.set(team_name, json.dumps(team_info))


def is_3bot_user(body_data):
    auth_response = urlopen("https://{}/api/users/{}".format(THREE_BOT_CONNECT_URL, body_data['doubleName']))
    data = json.loads(auth_response.read())
    user_public = data['publicKey']

    verify_key = nacl.signing.VerifyKey(user_public, encoder=nacl.encoding.Base64Encoder)

    try:
        verify_key.verify(base64.b64decode(body_data['signedAttempt']))
    except:
        return False
    return True
