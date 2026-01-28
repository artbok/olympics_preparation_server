from flask import Blueprint, request, jsonify
from services.user_service import * 


users_bp = Blueprint("users", __name__)

@users_bp.route('/getElo', methods=['POST'])
def new_user():
    data = request.json
    username = data["username"]
    user: User = getUser(username)
    return jsonify({'status': 'ok', "elo": user.rating})

@users_bp.route('/newUser', methods=['POST'])
def new_user():
    data = request.json
    if getUser(data["username"]):
        return jsonify({'status': 'userAlreadyExists'})
    createUser(data["username"], data["password"], data["rightsLevel"])
    return jsonify({'status': 'ok'})


@users_bp.route('/authUser', methods=['POST'])
def auth_user():
    data = request.json 
    if not isUser(data["username"], data["password"]):
        return jsonify({'status': 'invalidLogin'})
    user: User = getUser(data["username"])
    return jsonify({'status': 'ok', 'rightsLevel': user.rightsLevel})
