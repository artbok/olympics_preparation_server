from flask import Flask, request, jsonify,Blueprint
from datetime import datetime
import requests
import threading
import logging
import re
import json 
from routes.tasks import createTask
from models.task import Task

gig_bp = Blueprint("gig", __name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GigaChatAuthManager:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.expires_at = None 
        self.lock = threading.Lock()
    
    def _get_auth_header(self):
        return "MDE5YjM1YTMtNzFkOS03ZjFmLWIwMjAtN2M4MzIwZGY4NjJhOjdiNDczMTk3LTI1ZTctNGIwMy04MDlhLTg0YWQzZWQzMTU4ZA=="
        
    def get_token(self):
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        data = {"scope" : "GIGACHAT_API_PERS"}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': "f1ace353-28f1-41b1-a079-a08bd139944f",
            'Authorization': f'Basic {self._get_auth_header()}'
        }
        
        response = requests.post(url, headers=headers, data=data, verify=False)
        data = response.json()
        
        self.access_token = data['access_token']
        expires_timestamp = data["expires_at"] / 1000
        self.expires_at = datetime.fromtimestamp(expires_timestamp)
        
        logger.info(f"Token обновлен до: {self.expires_at}")
        return self.access_token
    
    def is_token_valid(self):
        if not self.access_token or not self.expires_at:
            return False
        return datetime.now() < self.expires_at
    
    def get_valid_token(self):
        with self.lock:
            if not self.is_token_valid():
                logger.info("Обновление токена...")
                self.get_token()
            return self.access_token


auth_manager = GigaChatAuthManager(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)


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
        
        token = auth_manager.get_valid_token()
        
        system_prompt = """Ты — генератор учебных задач. Сгенерируй ОДНУ задачу строго в формате JSON.
Формат:
{
  "subject": "название предмета",
  "topic": "тема",
  "difficulty": "Простой/Средний/Сложный",
  "description": "текст задачи",
  "hint": "подсказка",
  "answer": "ответ(ответ должен быть числом)",
  "explanation": "объяснение" (должно содержать ответ)
}"""
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        chat_data = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 1.0
        }
        
        response = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers=headers,
            json=chat_data,
            verify=False
        )
        
        result = response.json()
        
        if 'choices' not in result:
             return jsonify({'error': 'GigaChat error', 'details': result}), 500

        content = result['choices'][0]['message']['content']
        
        try:
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx == -1: raise ValueError("JSON not found")
            task_json = json.loads(content[start_idx:end_idx])
        except Exception:
            # Fallback (если вдруг JSON не распарсился)
            return jsonify({'error': 'Failed to parse JSON', 'content': content}), 500

        # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
        # Используем Task.create напрямую, так как она возвращает созданный объект
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
                'id': new_task.id,  # Теперь new_task — это объект, и id существует
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