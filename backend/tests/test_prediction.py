# test_prediction.py
import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from backend.routes.prediction import prediction_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.register_blueprint(prediction_bp, url_prefix='/api')
    return app

def test_get_history(client):
    token = create_access_token(identity='testuser')
    response = client.get('/api/history', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200

def test_save_feedback(client):
    token = create_access_token(identity='testuser')
    response = client.post('/api/feedback', json={'feedback': 'Great!'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
