from flask import Blueprint, request, jsonify
import logging
from models.task import Task
from services.generate_task_service import GigaChatAuthManager, GigaChatService

gig_bp = Blueprint("gig", __name__)
logger = logging.getLogger(__name__)

auth_manager = GigaChatAuthManager(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)

gigachat_service = GigaChatService(auth_manager)


@gig_bp.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'token_valid': auth_manager.is_token_valid()
    })


@gig_bp.route('/generate-task', methods=['POST'])
def generate_task():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        task_json = gigachat_service.generate_task(prompt)
        
        new_task = Task.create(
            subject=task_json.get('subject', 'Сгенерировано'),
            topic=task_json.get('topic', 'Общее'),
            difficulty=task_json.get('difficulty', 'Средний'),
            description=task_json.get('description', 'Ошибка описания'),
            hint=task_json.get('hint', ''),
            answer=task_json.get('answer', ''),
            explanation=task_json.get('explanation', '')
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
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@gig_bp.route('/token/status', methods=['GET'])
def token_status():
    return jsonify({
        'is_valid': auth_manager.is_token_valid(),
        'expires_at': auth_manager.expires_at.isoformat() if auth_manager.expires_at else None
    })


@gig_bp.route('/token/refresh', methods=['POST'])
def refresh_token():
    try:
        auth_manager.get_token()
        return jsonify({
            'success': True,
            'expires_at': auth_manager.expires_at.isoformat() if auth_manager.expires_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500