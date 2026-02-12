from datetime import datetime
import requests
import json 
from routes.tasks import createTask



class GigaChatAuthManager:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.expires_at = None
    
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
        if not self.is_token_valid():
            self.get_token()
        return self.access_token


auth_manager = GigaChatAuthManager(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)

def sendToGigachat(prompt):
    
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
"explanation": "объяснение (должно содержать ответ)"
}
"""
    print(system_prompt)
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
        "temperature": 1.3
    }
    
    response = requests.post(
        "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers=headers,
        json=chat_data,
        verify=False
    )
    
    result = response.json()
    content = result['choices'][0]['message']['content']
    start_idx = content.find('{')
    end_idx = content.rfind('}') + 1
    if start_idx == -1: raise ValueError("JSON not found")
    task_json = json.loads(content[start_idx:end_idx])

    new_task = createTask(
        task_json.get('subject', 'Сгенерировано'),
        task_json.get('topic', 'Общее'),
        task_json.get('difficulty', 'Средний'),
        task_json.get('description', 'Ошибка описания'),
        task_json.get('hint', ''),
        task_json.get('answer', ''),
        task_json.get('explanation', '')
    )
    return {
        'status': 'ok',
        'task': {
            'id': new_task.id,
            'description': new_task.description,
            'subject': new_task.subject,
            'difficulty': new_task.difficulty,
            'hint': new_task.hint,
            'answer': new_task.answer,
            'explanation': new_task.explanation
        }
    }
