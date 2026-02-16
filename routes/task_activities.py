from flask import Blueprint, request, jsonify
from services.user_service import * 
from services.task_activity_service import *

task_activities_bp = Blueprint("task_activities", __name__)

@task_activities_bp.route("/updateStatus", methods=["POST"])
def update_status():
    data = request.json
    status = isUser(data["username"], data["password"])
    if status == "ok":
        bindTaskWithUser(data["taskId"], getUser(data["username"].id))
    return jsonify({"status": status})

@task_activities_bp.route("/getUserTopicsStats", methods=["POST"])
def get_user_topics_stats():
    data = request.json
    status = isUser(data["username"], data["password"])
    
    if status == "ok":
        stats = getUserTopicsStats(data["username"])
        return jsonify({
            "status": status,
            "stats": stats
        })
    else:
        return jsonify({"status": status})
