import threading
import logging
from datetime import datetime
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GigaChatAuthManager:
    def __init__(self):
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
        return self.access_token
    
    def is_token_valid(self):
        if not self.access_token or not self.expires_at:
            return False
        return datetime.now() < self.expires_at
    
    def get_valid_token(self):
        with self.lock:
            if not self.is_token_valid():
                self.get_token()
            return self.access_token



class GigaChatService:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
    
    def generate_task(self, prompt):
        token = self.auth_manager.get_valid_token()
        
        system_prompt = open("prompt.txt", "r", encoding="utf-8").read()
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
            raise Exception(f"GigaChat error: {result}")
        
        content = result['choices'][0]['message']['content']
        
        try:
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx == -1:
                raise ValueError("JSON not found")
            task_json = json.loads(content[start_idx:end_idx])
            return task_json
        except Exception as e:
            raise Exception(f"Failed to parse JSON: {content}")