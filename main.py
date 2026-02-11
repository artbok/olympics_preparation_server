from flask import Flask
from routes.users import users_bp
from routes.tasks import tasks_bp
from routes.duels import duels_bp, socketio 
from routes.gig import gig_bp
from routes.admin import admin_stats_bp

app = Flask(__name__)
app.register_blueprint(users_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(duels_bp)
app.register_blueprint(gig_bp)
app.register_blueprint(admin_stats_bp, url_prefix='/admin')

socketio.init_app(app)

@app.after_request
def add_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')