from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import requests
import threading
import time
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
        with self.lock:
            url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            payload = "scope=GIGACHAT_API_PERS"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': "f1ace353-28f1-41b1-a079-a08bd139944f",
                'Authorization': f'Basic {self._get_auth_header()}'
            }
            
            response = requests.post(url, headers=headers, data=payload, verify=False)
            data = response.json()
            
            self.access_token = data['access_token']
            self.expires_at_ms = data["expires_at"]
            
            logger.info(f"Token обновлен до: {self.expires_at_ms}")
            return self.access_token
    
    def is_token_valid(self):
        if not self.access_token or not self.expires_at_ms:
            return False
        return datetime.now() < self.expires_at_ms
    
    def get_valid_token(self):
        with self.lock:
            if not self.is_token_valid():
                logger.info("Обновление токена...")
                self.get_token()
            return self.access_token

# Инициализация
auth_manager = GigaChatAuthManager(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'token_valid': auth_manager.is_token_valid()
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        token = auth_manager.get_valid_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        chat_data = {
            "model": "GigaChat",
            "messages": [{"role": "user", "content": message}],
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers=headers,
            json=chat_data,
            verify=False
        )
        
        if response.status_code == 401:
            # Повторная попытка с новым токеном
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
        return jsonify({
            'response': result['choices'][0]['message']['content'],
            'token_info': {
                'valid': auth_manager.is_token_valid(),
                'expires_at': auth_manager.expires_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/token/status', methods=['GET'])
def token_status():
    return jsonify({
        'is_valid': auth_manager.is_token_valid(),
        'expires_at': auth_manager.expires_at.isoformat() if auth_manager.expires_at else None
    })

@app.route('/token/refresh', methods=['POST'])
def refresh_token():
    try:
        auth_manager.get_token()
        return jsonify({
            'success': True,
            'expires_at': auth_manager.expires_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Получаем первый токен при запуске
    auth_manager.get_token()
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,
        threaded=True
    )