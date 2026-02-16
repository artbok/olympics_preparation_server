from flask import Blueprint, request, jsonify
from services.task_service import * 
from services.user_service import *
from services.task_activity_service import bindTaskWithUser

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/newTask", methods=["POST"])
def new_task():
    data = request.json
    status = isAdmin(data["username"], data["password"])
    if status == "ok":
        createTask(data["subject"], data["topic"], data["difficulty"], data["description"], data["hint"], data["answer"], data["explanation"])
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
                        "totalPages": countTasksPages(data.get("selectedTopics"), data.get("selectedDifficulties"))})
    return jsonify({"status": status})


@tasks_bp.route("/editTask", methods=["POST"])
def edit_task():
    data = request.json
    status = isAdmin(data["username"], data["password"])
    if status == "ok":
        editTask(data["taskId"], data["taskDescription"], data["taskSubject"], data["taskDifficulty"], data["taskHint"], data["taskAnswer"], data["taskExplanation"], data["taskTopic"])
    return jsonify({"status": status})

@tasks_bp.route("/editTaskActivitiesCorrect", methods=["POST"])
def edit_task_activities_correct():
    data = request.json
    status = isUser(data["username"], data["password"])
    user =  getUser(data["username"])
    if status == "ok":
        editTaskActivitiesCorrect(data["taskId"], user.id)
    return jsonify({"status": status})

@tasks_bp.route("/updateStatus", methods=["POST"])
def update_status():
    data = request.json
    status = isUser(data["username"], data["password"])
    if status == "ok":
        bindTaskWithUser(data["taskId"], getUser(data["username"].id))
    return jsonify({"status": status})

@tasks_bp.route('/upload', methods=['POST'])
def upload_task():
    if not request.is_json:
        return jsonify({"error": "Требуется JSON (Content-Type: application/json)"}), 400
    
    data = request.get_json()
    if isinstance(data, dict):
        tasks_list = [data]
    elif isinstance(data, list):
        tasks_list = data
    else:
        return jsonify({"error": "Тело запроса должно быть объектом задачи или массивом задач"}), 400

    if not tasks_list:
        return jsonify({"error": "Список задач не может быть пустым"}), 400

    REQUIRED_FIELDS = [
        'description', 'hint', 'answer', 'explanation',
        'difficulty', 'subject', 'topic'
    ]
    
    results = []
    success_count = 0

    for idx, task_data in enumerate(tasks_list):
        if not isinstance(task_data, dict):
            results.append({
                "index": idx,
                "status": "error",
                "error": "Элемент должен быть объектом задачи"
            })
            continue

        missing = [field for field in REQUIRED_FIELDS if field not in task_data]
        if missing:
            results.append({
                "index": idx,
                "status": "error",
                "error": f"Отсутствуют поля: {', '.join(missing)}"
            })
            continue

        task = createTask(
            description=task_data['description'],
            hint=task_data['hint'],
            answer=task_data['answer'],
            explanation=task_data['explanation'],
            difficulty=task_data['difficulty'],
            subject=task_data['subject'],
            topic=task_data['topic']
        )
        results.append({
            "index": idx,
            "status": "success",
            "task_id": task.id,
            "message": "Задача успешно добавлена"
        })
        success_count += 1


    response_data = {
        "total": len(tasks_list),
        "success_count": success_count,
        "results": results
    }
    
    return jsonify(response_data), 200