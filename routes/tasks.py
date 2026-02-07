from flask import Blueprint, request, jsonify
from services.task_service import * 
from services.user_service import *


tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/newTask", methods=["POST"])
def new_task():
    data = request.json
    status = isAdmin(data["username"], data["password"])
    if status == "ok":
        createTask(data["subject"], data["topic"], data["difficulty"], data["description"], data["hint"], data["answer"])
    return jsonify({"status": status})


@tasks_bp.route("/deleteTask", methods=["POST"])
def delete_task():
    data = request.json
    status = isAdmin(data["username"], data["password"])
    if status == "ok":
        deleteTask(data["taskId"])
    return jsonify({"status": status})


@tasks_bp.route("/getTasks", methods=["POST"])
def get_tasks():
    data = request.json
    status = isUser(data["username"], data["password"])
    if status:
        return getTasks(data["subject"], data["topic"], data["difficulty"], data["description"], data["page"])
    return jsonify({"status": "wrong_credentials"})