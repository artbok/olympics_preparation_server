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

@users_bp.route('/editUser', methods=['POST'])
def edit_user():
    data = request.json
    status = isAdmin(data["username"], data["password"])
    if status == "ok":
        editUser(data["editUserName"])
    return jsonify({"status": status})

@users_bp.route('/deleteUser', methods=['POST'])
def delete_user():
    data = request.json
    status = isAdmin(data["username"], data["password"])
    if status == "ok":
        deleteUser(data["deleteUserName"])
    return jsonify({"status": status})

@users_bp.route('/authUser', methods=['POST'])
def auth_user():
    data = request.json 
    status = isUser(data["username"], data["password"])
    if status == "ok":
        user: User = getUser(data["username"])
        return jsonify({'status': status, 'rightsLevel': user.rightsLevel})
    return jsonify({'status': status})

@users_bp.route('/getProfile', methods=['POST'])
def get_profile():
    try:
        data = request.json

        if not data or 'username' not in data:
            return jsonify({"error": "Invalid request"}), 400
        
        username = data['username']
        profile_data = getProfile(username)
        
        if 'error' in profile_data:
            return jsonify(profile_data), 404
            
        return jsonify(profile_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500