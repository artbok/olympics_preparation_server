from flask import Blueprint, request, jsonify
from services.user_service import * 


users_bp = Blueprint("users", __name__)

@users_bp.route('/getRating', methods=['POST'])
def get_rating():
    data = request.json
    username = data["username"]
    user: User = getUser(username)
    return jsonify({'status': 'ok', "rating": user.rating})


@users_bp.route('/newUser', methods=['POST'])
def new_user():
    data = request.json
    status = createUser(data["username"], data["password"], data["rightsLevel"])
    return jsonify({'status': status})


@users_bp.route('/authUser', methods=['POST'])
def auth_user():
    data = request.json 
    if not isUser(data["username"], data["password"]):
        return jsonify({'status': 'invalidLogin'})
    user: User = getUser(data["username"])
    return jsonify({'status': 'ok', 'rightsLevel': user.rightsLevel})
