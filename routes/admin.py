# admin_stats.py
from flask import Blueprint, request, jsonify, Response
from services.user_service import isAdmin
from services.admin_service import get_user_stats, get_all_users_stats

admin_stats_bp = Blueprint("admin_stats", __name__)

@admin_stats_bp.route('/stats', methods=['POST'])
def admin_stats():
    data = request.json
    
    if isAdmin(data.get("username"), data.get("password")) != "ok":
        return jsonify({"status": "access_denied"}), 403
    
    if data.get("type") == "user":
        user = data.get("user")
        return jsonify(get_user_stats(user)) if user else jsonify({"error": "user required"}), 400
    
    return jsonify(get_all_users_stats())