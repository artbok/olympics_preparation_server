from flask import Blueprint, request, jsonify
from services.task_service import * 
from services.user_service import *


tasks_bd = Blueprint("tasks", __name__)

@tasks_bd.route("/newTask", methods=["POST"])
def new_task():
    data = request.json
    status = isAdmin(data["username"], data["password"])
    if status == "ok":
        task = createTask(data["subject"], data["topic"], data["difficulty"], data["description"], data["hint"], data["answer"])
    return jsonify({"status": status})


@tasks_bd.route("/deleteTask", methods=["POST"])
def delete_task():
    data = request.json
    status = isAdmin(data["username"], data["password"])
    if status == "ok":
        task: Task = Task.get_by_id(data["taskId"])
        deleteTask(data["taskId"])
    return jsonify({"status": status})

@tasks_bd.route("/getTasks", methods=["POST"])
def get_tasks():
    data = request.json
    status = isUser(data["username"], data["password"])
    print(status)
    if status:
        return getTasks(data["subject"], data["topic"], data["difficulty"], data["description"], data["page"])
    return "notAuth"



    
    
