from flask import request, jsonify, Blueprint
from services.task_service import *

tasks_bp = Blueprint("tasks", __name__)

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