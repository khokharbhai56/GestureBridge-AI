# prediction.py
# Endpoints for saving and retrieving prediction history and feedback

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from datetime import datetime
from bson.objectid import ObjectId

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    history = list(db.get_collection('history').find({'user_id': user_id}))
    for item in history:
        item['_id'] = str(item['_id'])
    return jsonify({'history': history})

@prediction_bp.route('/history', methods=['POST'])
@jwt_required()
def save_history():
    user_id = get_jwt_identity()
    data = request.get_json()
    db.get_collection('history').insert_one({
        'user_id': user_id,
        'prediction': data.get('prediction'),
        'timestamp': datetime.utcnow()
    })
    return jsonify({'message': 'History saved'})

@prediction_bp.route('/feedback', methods=['POST'])
@jwt_required()
def save_feedback():
    user_id = get_jwt_identity()
    data = request.get_json()
    db.get_collection('feedback').insert_one({
        'user_id': user_id,
        'feedback': data.get('feedback'),
        'timestamp': datetime.utcnow()
    })
    return jsonify({'message': 'Feedback saved'})

@prediction_bp.route('/history', methods=['DELETE'])
@jwt_required()
def delete_history():
    user_id = get_jwt_identity()
    db.get_collection('history').delete_many({'user_id': user_id})
    return jsonify({'message': 'History deleted'})

@prediction_bp.route('/account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    db.get_collection('users').delete_one({'_id': ObjectId(user_id)})
    db.get_collection('history').delete_many({'user_id': user_id})
    db.get_collection('feedback').delete_many({'user_id': user_id})
    return jsonify({'message': 'Account deleted'})
