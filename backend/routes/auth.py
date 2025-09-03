from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging
import sys
import os

# Fix import error by adding backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from database import db
from bson import ObjectId

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Check if user already exists
        users = db.get_collection('users')
        if users.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already registered'}), 409
            
        if users.find_one({'username': data['username']}):
            return jsonify({'error': 'Username already taken'}), 409
            
        # Assign role (admin if username is 'admin', else user)
        role = 'admin' if data['username'].lower() == 'admin' else 'user'
        new_user = {
            'username': data['username'],
            'email': data['email'],
            'password': generate_password_hash(data['password']),
            'role': role,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = users.insert_one(new_user)
        access_token = create_access_token(identity=str(result.inserted_id))
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'role': role
        }), 201
        
    except Exception as e:
        logger.error(f"Error in registration: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(field in data for field in ['email', 'password']):
            return jsonify({'error': 'Missing email or password'}), 400
            
        # Find user
        users = db.get_collection('users')
        user = users.find_one({'email': data['email']})
        
        if not user or not check_password_hash(user['password'], data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
            
        # Create access token
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'role': user.get('role', 'user'),
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user.get('role', 'user'),
                'created_at': user.get('created_at'),
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Admin dashboard endpoint to list all users
@auth_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def list_users():
    user_id = get_jwt_identity()
    users = db.get_collection('users')
    current_user = users.find_one({'_id': ObjectId(user_id)})
    if not current_user or current_user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    user_list = []
    for u in users.find():
        user_list.append({
            'id': str(u['_id']),
            'username': u['username'],
            'email': u['email'],
            'role': u.get('role', 'user'),
            'created_at': u.get('created_at'),
        })
    return jsonify({'users': user_list}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        
        users = db.get_collection('users')
        user = users.find_one({'_id': ObjectId(current_user_id)})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at'].isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        users = db.get_collection('users')
        user = users.find_one({'_id': ObjectId(current_user_id)})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Update allowed fields
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        if 'username' in data:
            # Check if username is already taken by another user
            existing_user = users.find_one({
                'username': data['username'],
                '_id': {'$ne': ObjectId(current_user_id)}
            })
            if existing_user:
                return jsonify({'error': 'Username already taken'}), 409
            update_data['username'] = data['username']
            
        if 'password' in data:
            update_data['password'] = generate_password_hash(data['password'])
            
        # Update user
        users.update_one(
            {'_id': ObjectId(current_user_id)},
            {'$set': update_data}
        )
        
        return jsonify({
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
