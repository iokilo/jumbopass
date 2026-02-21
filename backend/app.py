import sys
import os
from dotenv import load_dotenv
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory
from api.auth import auth_bp
from api.vault import vault_bp

app = Flask(__name__, static_folder='../frontend', static_url_path='')

app.register_blueprint(auth_bp)
app.register_blueprint(vault_bp)

load_dotenv()
app.secret_key = os.environ["SECRET_KEY"]

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)