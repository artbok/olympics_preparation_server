from flask import Blueprint, request, jsonify
from services.generate_task_service import GigaChatAuthManager, GigaChatService
from services.task_service import createTask


generate_task_bp = Blueprint("generate_task", __name__)

auth_manager = GigaChatAuthManager()
gigachat_service = GigaChatService(auth_manager)


@generate_task_bp.route('/generate-task', methods=['POST'])
def generate_task():
    data = request.get_json()
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    task_json = gigachat_service.generate_task(prompt)
    
    new_task = createTask(
        task_json.get('subject', 'Сгенерировано'),
        task_json.get('topic', 'Общее'),
        task_json.get('difficulty', 'Средний'),
        task_json.get('description', 'Ошибка описания'),
        task_json.get('hint', ''),
        task_json.get('answer', ''),
        task_json.get('explanation', '')
    )
    
    return jsonify({
        'success': True,
        'task': {
            'id': new_task.id,
            'description': new_task.description,
            'subject': new_task.subject,
            'difficulty': new_task.difficulty,
            'hint': new_task.hint,
            'answer': new_task.answer,
            'explanation': new_task.explanation
        }
    })