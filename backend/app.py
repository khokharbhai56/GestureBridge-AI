import sys
import os

# Fix import error by adding backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from database import db
from routes.auth import auth_bp
from routes.streaming import streaming_bp
from routes.feedback import feedback_bp
from routes.run_gui import gui_bp
from routes.chat import chat_bp

# ✅ Create Flask app before using @app.route
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
app.config.from_object(Config)

# ✅ Setup extensions
jwt = JWTManager(app)
CORS(app)

# ✅ Connect to MongoDB
db.connect()

# ✅ Register routes
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(streaming_bp, url_prefix='/api/streaming')
app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
app.register_blueprint(gui_bp, url_prefix='/api/gui')
app.register_blueprint(chat_bp, url_prefix='/api/chat')

# ✅ Home route serving frontend index.html
@app.route('/')
def home():
    # Redirect to /index.html explicitly to avoid directory listing issues
    return send_from_directory(app.static_folder, 'index.html')

# Redirect route to handle root URL with trailing slash
@app.route('/index.html/')
def index_html_slash():
    return send_from_directory(app.static_folder, 'index.html')

# ✅ Catch-all route to serve index.html for frontend routes (SPA support)
@app.route('/<path:path>')
def catch_all(path):
    if path != "" and (path.startswith('api') or path.startswith('backend')):
        # Let backend handle API or backend routes normally
        return "Not Found", 404
    # Check if path is a static file by extension
    if '.' in path:
        return send_from_directory(app.static_folder, path)
    # Redirect to index.html for SPA routes without extension
    return send_from_directory(app.static_folder, 'index.html')

# Redirect route to handle trailing slash on root URL
@app.route('/index.html')
def index_html():
    return send_from_directory(app.static_folder, 'index.html')

# ✅ Run the app
if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT)
