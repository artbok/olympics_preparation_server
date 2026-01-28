from flask import Flask
from routes.users import users_bp
from routes.tasks import tasks_bd

app = Flask(__name__)
app.register_blueprint(users_bp)
app.register_blueprint(tasks_bd)
    

@app.after_request
def add_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

app.run(host='0.0.0.0') 