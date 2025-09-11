from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import cv2
import numpy as np
from datetime import datetime
import sys
import os

# Fix import error by adding backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from database import db
from config import Config
import openai


streaming_bp = Blueprint('streaming', __name__)

@streaming_bp.route('/start', methods=['POST'])
@jwt_required()
def start_streaming():
    """Start a new streaming session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        language = data.get('language', 'ASL')
        quality = data.get('quality', 'medium')  # low, medium, high
        
        # Create session data
        session_data = {
            'session_id': f"stream_{user_id}_{datetime.now().timestamp()}",
            'language': language,
            'quality': quality,
            'device_type': data.get('device_type'),
            'browser': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr
        }
        
        # Create streaming session in MongoDB
        streaming_model = db.get_model('streaming_sessions')
        session_id = streaming_model.create_session(user_id, session_data)
        
        # Log analytics event
        analytics_model = db.get_model('analytics')
        analytics_model.log_event(user_id, {
            'event_type': 'streaming',
            'event_name': 'session_start',
            'properties': {
                'session_id': session_data['session_id'],
                'language': language,
                'quality': quality
            }
        })
        
        return jsonify({
            'success': True,
            'session_id': session_data['session_id'],
            'language': language,
            'quality': quality,
            'message': 'Streaming session started successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@streaming_bp.route('/process_frame', methods=['POST'])
@jwt_required()
def process_frame():
    """Process a single video frame for sign language recognition"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        session_id = data.get('session_id')
        frame_data = data.get('frame')  # Base64 encoded frame
        timestamp = data.get('timestamp')
        
        # Get session from MongoDB
        streaming_model = db.get_model('streaming_sessions')
        session = streaming_model.get_session(session_id)
        
        if not session or session['user_id'] != user_id:
            return jsonify({'error': 'Invalid session ID or unauthorized'}), 400
        
        if session['status'] != 'active':
            return jsonify({'error': 'Session is not active'}), 400
        
        # Decode frame
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        
        # Process frame with ML model (placeholder)
        translation_result = process_sign_language_frame(frame, session['language'])
        
        # Update session statistics
        update_data = {
            'frame_count': session['statistics']['total_frames'] + 1,
            'translation': {
                'text': translation_result['translation'],
                'refined_text': translation_result.get('refined_translation', translation_result['translation']),
                'confidence': translation_result['confidence'],
                'timestamp': timestamp
            }
        }
        
        streaming_model.update_session(session_id, update_data)
        
        # Log analytics event
        analytics_model = db.get_model('analytics')
        analytics_model.log_event(user_id, {
            'event_type': 'streaming',
            'event_name': 'frame_processed',
            'properties': {
                'session_id': session_id,
                'confidence': translation_result['confidence'],
                'language': session['language']
            }
        })
        
        return jsonify({
            'success': True,
            'translation': translation_result['translation'],
            'refined_translation': translation_result.get('refined_translation', translation_result['translation']),
            'confidence': translation_result['confidence'],
            'language': session['language'],
            'frame_count': session['statistics']['total_frames'] + 1
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@streaming_bp.route('/stop/<session_id>', methods=['POST'])
@jwt_required()
def stop_streaming(session_id):
    """Stop a streaming session"""
    try:
        user_id = get_jwt_identity()
        
        # Get session from MongoDB
        streaming_model = db.get_model('streaming_sessions')
        session = streaming_model.get_session(session_id)
        
        if not session:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        if str(session['user_id']) != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if session['status'] != 'active':
            return jsonify({'error': 'Session is already stopped'}), 400
        
        # Calculate final statistics
        duration = (datetime.now() - session['created_at']).total_seconds()
        final_stats = {
            'total_frames': session['statistics']['total_frames'],
            'total_translations': len(session['translations']),
            'duration_seconds': duration,
            'average_confidence': sum(t['confidence'] for t in session['translations']) / len(session['translations']) if session['translations'] else 0
        }
        
        # End session in MongoDB
        streaming_model.end_session(session_id, final_stats)
        
        # Log analytics event
        analytics_model = db.get_model('analytics')
        analytics_model.log_event(user_id, {
            'event_type': 'streaming',
            'event_name': 'session_end',
            'properties': {
                'session_id': session_id,
                'duration': duration,
                'total_frames': final_stats['total_frames'],
                'total_translations': final_stats['total_translations'],
                'average_confidence': final_stats['average_confidence']
            }
        })
        
        return jsonify({
            'success': True,
            'session_summary': final_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@streaming_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions():
    """Get active streaming sessions for the current user"""
    try:
        user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status', 'active')  # active, completed, all
        
        # Get sessions from MongoDB
        streaming_model = db.get_model('streaming_sessions')
        result = streaming_model.get_user_sessions(user_id, status, page, per_page)
        
        # Log analytics event
        analytics_model = db.get_model('analytics')
        analytics_model.log_event(user_id, {
            'event_type': 'streaming',
            'event_name': 'view_sessions',
            'properties': {
                'status': status,
                'page': page,
                'total_sessions': result['total']
            }
        })
        
        return jsonify({
            'success': True,
            'sessions': result['sessions'],
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'total_pages': result['total_pages']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def refine_translation_with_chatgpt(basic_translation, language, context=None):
    """
    Refine basic translation using ChatGPT for more natural language
    """
    try:
        if not Config.OPENAI_API_KEY:
            return basic_translation  # Return basic if no API key

        openai.api_key = Config.OPENAI_API_KEY

        prompt = f"Refine this sign language translation to make it more natural and conversational: '{basic_translation}'. Language: {language}."
        if context:
            prompt += f" Context: {context}"

        response = openai.ChatCompletion.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that refines sign language translations into natural, conversational language."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )

        refined = response.choices[0].message.content.strip()
        return refined if refined else basic_translation

    except Exception as e:
        print(f"Error refining translation: {e}")
        return basic_translation  # Fallback to basic translation

def process_sign_language_frame(frame, language):
    """
    Process video frame for sign language recognition
    This is a placeholder - integrate with actual ML model
    """
    # Placeholder implementation
    import random

    sample_translations = {
        'ASL': ['Hello', 'Thank you', 'Please', 'Yes', 'No', 'Good morning', 'How are you?'],
        'BSL': ['Hello', 'Cheers', 'Please', 'Yes', 'No', 'Good morning', 'How are you?'],
        'JSL': ['こんにちは', 'ありがとう', 'お願いします', 'はい', 'いいえ', 'おはよう', '元気ですか？'],
        'LSF': ['Bonjour', 'Merci', 'S\'il vous plaît', 'Oui', 'Non', 'Bonjour', 'Comment allez-vous?'],
        'DGS': ['Hallo', 'Danke', 'Bitte', 'Ja', 'Nein', 'Guten Morgen', 'Wie geht es Ihnen?']
    }

    translations = sample_translations.get(language, sample_translations['ASL'])
    basic_translation = random.choice(translations)
    confidence = round(random.uniform(0.85, 0.99), 3)

    # Refine translation using ChatGPT
    refined_translation = refine_translation_with_chatgpt(basic_translation, language)

    return {
        'translation': basic_translation,
        'refined_translation': refined_translation,
        'confidence': confidence
    }
