from flask import request, jsonify,Blueprint
from services.task_generation_service import sendToGigachat

gen_bp = Blueprint("generate_task", __name__)


@gen_bp.route('/generate-task', methods=['POST'])
def generate_task():
    data = request.get_json()
    prompt = data.get('prompt')
    return jsonify(sendToGigachat(prompt))