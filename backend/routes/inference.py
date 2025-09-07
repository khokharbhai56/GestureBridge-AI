from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import numpy as np
import tempfile
import os
from datetime import datetime
from backend.database import db

from backend.sign_language_app.model import SignLanguageModel
from bson import ObjectId

logger = logging.getLogger(__name__)
inference_bp = Blueprint('inference', __name__)

# Initialize the model
sign_language_model = SignLanguageModel()

@inference_bp.route('/process-video', methods=['POST'])
@jwt_required()
def process_video():
    try:
        current_user_id = get_jwt_identity()
        
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
            
        video_file = request.files['video']
        
        # Save video file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            video_file.save(temp_video.name)
            
            try:
                # Process video and extract landmarks
                landmarks = sign_language_model.preprocess_video(temp_video.name)
                
                if not landmarks:
                    return jsonify({'error': 'No hand gestures detected in video'}), 400
                    
                # Convert landmarks to numpy array and make prediction
                landmarks_array = np.array(landmarks)
                predictions = sign_language_model.predict(landmarks_array)
                
                # Get the most common prediction across frames
                predicted_class = np.bincount(np.argmax(predictions, axis=1)).argmax()
                confidence = float(np.mean(predictions[:, predicted_class]))
                
                # Save the translation to database
                translations = db.get_collection('translations')
                translation_record = {
                    'user_id': ObjectId(current_user_id),
                    'type': 'video',
                    'predicted_class': int(predicted_class),
                    'confidence': confidence,
                    'created_at': datetime.utcnow()
                }
                translations.insert_one(translation_record)
                
                return jsonify({
                    'predicted_class': int(predicted_class),
                    'confidence': confidence,
                    'message': 'Video processed successfully'
                }), 200
                
            finally:
                # Clean up temporary file
                os.unlink(temp_video.name)
                
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@inference_bp.route('/process-text', methods=['POST'])
@jwt_required()
def process_text():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text']
        
        # TODO: Implement text-to-sign conversion
        # This would typically involve:
        # 1. Text preprocessing
        # 2. Converting text to sign language sequences
        # 3. Generating visual representations or instructions
        
        # For now, return a mock response
        translation_record = {
            'user_id': ObjectId(current_user_id),
            'type': 'text',
            'input_text': text,
            'created_at': datetime.utcnow()
        }
        
        translations = db.get_collection('translations')
        translations.insert_one(translation_record)
        
        return jsonify({
            'message': 'Text processed successfully',
            'result': 'Text to sign conversion will be implemented in future updates'
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@inference_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    try:
        current_user_id = get_jwt_identity()
        
        # Get page parameters for pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Calculate skip value for pagination
        skip = (page - 1) * per_page
        
        translations = db.get_collection('translations')
        
        # Get total count for pagination
        total_count = translations.count_documents({'user_id': ObjectId(current_user_id)})
        
        # Get paginated results
        results = translations.find(
            {'user_id': ObjectId(current_user_id)}
        ).sort(
            'created_at', -1
        ).skip(skip).limit(per_page)
        
        # Convert results to list and format dates
        history_list = []
        for record in results:
            record['_id'] = str(record['_id'])
            record['user_id'] = str(record['user_id'])
            record['created_at'] = record['created_at'].isoformat()
            history_list.append(record)
            
        return jsonify({
            'history': history_list,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@inference_bp.route('/history/<translation_id>', methods=['GET'])
@jwt_required()
def get_translation_detail(translation_id):
    try:
        current_user_id = get_jwt_identity()
        
        translations = db.get_collection('translations')
        translation = translations.find_one({
            '_id': ObjectId(translation_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not translation:
            return jsonify({'error': 'Translation not found'}), 404
            
        # Format the translation record
        translation['_id'] = str(translation['_id'])
        translation['user_id'] = str(translation['user_id'])
        translation['created_at'] = translation['created_at'].isoformat()
        
        return jsonify(translation), 200
        
    except Exception as e:
        logger.error(f"Error fetching translation detail: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
