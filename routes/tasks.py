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
    if status == "ok":
        return jsonify({"status": status, 
                        "tasks": getTasks(data["page"], data.get("selectedTopics"), data.get("selectedDifficulties")), 
                        "topics": getTopics(),
                        "totalPages": countTasksPages()})
    return jsonify({"status": status})


@tasks_bp.route("/editTask", methods=["POST"])
def edit_task():
    data = request.json
    status = isAdmin(data["username"], data["password"])
    if status == "ok":
        editTask(data["taskId"], data["taskDescription"], data["taskSubject"], data["taskDifficulty"], data["taskHint"], data["taskAnswer"], data["taskTopic"])
    return jsonify({"status": status})


@tasks_bp.route('/upload', methods=['POST'])
def upload_task():
    if not request.is_json:
        return jsonify({"error": "Требуется JSON (Content-Type: application/json)"}), 400
    
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({"error": f"Ошибка парсинга JSON: {str(e)}"}), 400
    
    REQUIRED_FIELDS = [
        'description', 'hint', 'answer',
        'difficulty', 'subject', 'topic'
    ]
    

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        return jsonify({
            "error": f"Отсутствуют обязательные поля: {', '.join(missing)}",
            "required_fields": REQUIRED_FIELDS
        }), 400
        
    try:
        task_id = createTask(
            description=data['description'],
            hint=data['hint'],
            answer=data['answer'],
            difficulty=data['difficulty'],
            subject=data['subject'],
            topic=data['topic']
        )
        
        return jsonify({
            "success": True,
            "message": "Задача успешно добавлена",
            "task_id": task_id
        }), 201
    
    except Exception as e:
        print(f"[SERVER ERROR] createTask failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Ошибка при сохранении задачи",
            "details": str(e) if tasks_bp.debug else None
        }), 500
