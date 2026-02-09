from flask import Flask, request, jsonify,Blueprint
from datetime import datetime
import requests
import threading
import logging
import re
import json 
from routes.tasks import createTask

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
        system_prompt = """Ты — генератор учебных задач. Сгенерируй ОДНУ задачу в СТРОГОМ формате JSON.

Формат задачи:
{{
  название предмета
  тема задачи
  Уровень лёгкий/средний/сложный
  Полное условие задачи
  Подсказка: краткая подсказка для решения
  Ответ: нужен правильный ответ задачи, без решения
}}

ВАЖНО:
- Отвечай ТОЛЬКО валидным JSON объектом (не массив!)
- Не добавляй никакого другого текста до или после JSON
- Сгенерируй ровно ОДНУ задачу
- Все поля обязательны, не оставляй их пустыми"""
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        chat_data = {
            "model": "GigaChat",
            "messages": [
                {"role": "system"},
                {"role": "user", "content": f"Сгенерируй задачи: {prompt} и {system_prompt}"}
            ],
        }
        
        response = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers=headers,
            json=chat_data,
            verify=False
        )
        
        if response.status_code == 401:
            auth_manager.get_token()
            token = auth_manager.get_valid_token()
            headers['Authorization'] = f'Bearer {token}'
            
            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                headers=headers,
                json=chat_data,
                verify=False
            )
        
        result = response.json()  
        answer = result['choices'][0]['message']['content']
        answer = re.sub(r'[#\$\{\}\"]+', '', answer, flags=re.DOTALL)
        tasks = [line.strip() for line in answer.split('\n') if line.strip()]
        
        return jsonify({
            'tasks': tasks
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