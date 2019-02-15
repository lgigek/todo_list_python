from flask import Flask
from routes.task_routes import task
from log import log_formatter

if __name__ == '__main__':
    app = Flask(__name__)

    app.register_blueprint(task, url_prefix='/task')

    # Disable flask jsonify from sorting alphabetically
    app.config['JSON_SORT_KEYS'] = False
    app.run(host='0.0.0.0')