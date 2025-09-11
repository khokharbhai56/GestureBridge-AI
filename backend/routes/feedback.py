from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os

# Fix import error by adding backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from database import db
from config import Config
import openai


feedback_bp = Blueprint('feedback', __name__)

def analyze_feedback_with_chatgpt(feedback_data):
    """
    Analyze user feedback using ChatGPT to provide insights and suggestions
    """
    try:
        if not Config.OPENAI_API_KEY:
            return {
                'analysis': 'Feedback analysis requires OpenAI API key',
                'suggestions': ['Set up OpenAI API key for automated feedback analysis'],
                'sentiment': 'neutral'
            }

        openai.api_key = Config.OPENAI_API_KEY

        feedback_type = feedback_data.get('type', 'general')
        rating = feedback_data.get('rating', 3)
        comment = feedback_data.get('comment', '')
        category = feedback_data.get('category', 'general')

        prompt = f"""Analyze this user feedback for GestureBridge AI sign language translation app:

Feedback Type: {feedback_type}
Rating: {rating}/5
Category: {category}
Comment: {comment}

Please provide:
1. Sentiment analysis (positive, negative, neutral)
2. Key insights from the feedback
3. Specific suggestions for improvement
4. Priority level (low, medium, high)

Format the response as JSON with keys: sentiment, insights, suggestions, priority"""

        response = openai.ChatCompletion.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an AI assistant that analyzes user feedback for a sign language translation app. Provide structured analysis in JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )

        analysis_text = response.choices[0].message.content.strip()

        # Try to parse as JSON, fallback to text analysis
        try:
            import json
            analysis = json.loads(analysis_text)
        except:
            # Fallback parsing
            analysis = {
                'sentiment': 'neutral',
                'insights': [analysis_text],
                'suggestions': ['Review feedback manually'],
                'priority': 'medium'
            }

        return analysis

    except Exception as e:
        print(f"Feedback analysis error: {e}")
        return {
            'analysis': f'Error analyzing feedback: {str(e)}',
            'suggestions': ['Manual review recommended'],
            'sentiment': 'neutral'
        }

@feedback_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_feedback():
    """Submit user feedback for translation accuracy"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        feedback_type = data.get('type')  # 'translation', 'accuracy', 'feature', 'bug'
        rating = data.get('rating')  # 1-5 scale
        comment = data.get('comment', '')
        translation_id = data.get('translation_id')
        suggested_correction = data.get('suggested_correction')
        
        if not feedback_type or rating is None:
            return jsonify({'error': 'Feedback type and rating are required'}), 400
        
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        feedback_data = {
            'type': feedback_type,
            'rating': rating,
            'comment': comment,
            'translation_id': translation_id,
            'suggested_correction': suggested_correction,
            'category': data.get('category', 'general'),
            'severity': data.get('severity', 'medium'),
            'browser_info': request.headers.get('User-Agent'),
            'device_info': data.get('device_info'),
            'url': request.referrer
        }

        # Analyze feedback with ChatGPT if comment is provided
        analysis = None
        if comment and len(comment.strip()) > 0:
            analysis = analyze_feedback_with_chatgpt(feedback_data)
            feedback_data['ai_analysis'] = analysis
        
        feedback_model = db.get_model('feedback')
        feedback_id = feedback_model.create_feedback(user_id, feedback_data)
        
        # Log analytics event
        analytics_model = db.get_model('analytics')
        analytics_model.log_event(user_id, {
            'event_type': 'feedback',
            'event_name': 'submit_feedback',
            'properties': {
                'feedback_type': feedback_type,
                'rating': rating,
                'feedback_id': str(feedback_id)
            }
        })
        
        response_data = {
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': str(feedback_id)
        }

        if analysis:
            response_data['ai_analysis'] = analysis

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/analyze/<feedback_id>', methods=['POST'])
@jwt_required()
def analyze_feedback(feedback_id):
    """Analyze existing feedback using ChatGPT"""
    try:
        user_id = get_jwt_identity()

        feedback_model = db.get_model('feedback')
        feedback = feedback_model.get_feedback_by_id(feedback_id)

        if not feedback:
            return jsonify({'error': 'Feedback not found'}), 404

        # Check if user owns the feedback or is admin
        if str(feedback['user_id']) != user_id:
            # TODO: Add admin check
            return jsonify({'error': 'Unauthorized to analyze this feedback'}), 403

        # Analyze the feedback
        analysis = analyze_feedback_with_chatgpt(feedback)

        # Update feedback with analysis
        feedback_model.update_feedback(feedback_id, {'ai_analysis': analysis})

        return jsonify({
            'success': True,
            'analysis': analysis,
            'message': 'Feedback analyzed successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/translation', methods=['POST'])
@jwt_required()
def submit_translation_feedback():
    """Submit specific feedback for a translation"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        translation_id = data.get('translation_id')
        original_text = data.get('original_text')
        suggested_text = data.get('suggested_text')
        accuracy_rating = data.get('accuracy_rating')  # 1-5
        language = data.get('language')
        confidence_score = data.get('confidence_score')
        
        if not all([translation_id, accuracy_rating, language]):
            return jsonify({'error': 'Translation ID, accuracy rating, and language are required'}), 400
        
        feedback_data = {
            'type': 'translation',
            'category': 'accuracy',
            'rating': accuracy_rating,
            'translation_id': translation_id,
            'suggested_correction': suggested_text,
            'language': language,
            'comment': data.get('comment', ''),
            'browser_info': request.headers.get('User-Agent'),
            'device_info': data.get('device_info'),
            'metadata': {
                'original_text': original_text,
                'confidence_score': confidence_score
            }
        }
        
        feedback_model = db.get_model('feedback')
        feedback_id = feedback_model.create_feedback(user_id, feedback_data)
        
        # Update translation feedback
        translations_model = db.get_model('translations')
        translations_model.update_feedback(translation_id, {
            'accuracy_rating': accuracy_rating,
            'user_correction': suggested_text,
            'feedback_id': str(feedback_id)
        })
        
        return jsonify({
            'success': True,
            'message': 'Translation feedback submitted successfully',
            'feedback_id': str(feedback_id)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/my-feedback', methods=['GET'])
@jwt_required()
def get_user_feedback():
    """Get all feedback submitted by the current user"""
    try:
        user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        feedback_model = db.get_model('feedback')
        result = feedback_model.get_user_feedback(user_id, page, per_page)
        
        return jsonify({
            'success': True,
            'feedback': result['feedback'],
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'total_pages': result['total_pages']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/statistics', methods=['GET'])
def get_feedback_statistics():
    """Get overall feedback statistics"""
    try:
        feedback_model = db.get_model('feedback')
        stats = feedback_model.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/improve-model', methods=['POST'])
@jwt_required()
def contribute_to_model_improvement():
    """Allow users to contribute data for model improvement"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        contribution_type = data.get('type')  # 'video_sample', 'correction', 'new_gesture'
        language = data.get('language')
        gesture_description = data.get('gesture_description')
        video_data = data.get('video_data')  # Base64 encoded video
        correct_translation = data.get('correct_translation')
        
        if not all([contribution_type, language]):
            return jsonify({'error': 'Contribution type and language are required'}), 400
        
        feedback_data = {
            'type': 'model_improvement',
            'category': contribution_type,
            'language': language,
            'comment': gesture_description,
            'metadata': {
                'correct_translation': correct_translation,
                'video_data': video_data
            }
        }
        
        feedback_model = db.get_model('feedback')
        feedback_id = feedback_model.create_feedback(user_id, feedback_data)
        
        # Log analytics event
        analytics_model = db.get_model('analytics')
        analytics_model.log_event(user_id, {
            'event_type': 'model_improvement',
            'event_name': 'contribution',
            'properties': {
                'contribution_type': contribution_type,
                'language': language,
                'feedback_id': str(feedback_id)
            }
        })
        
        return jsonify({
            'success': True,
            'message': 'Thank you for contributing to model improvement!',
            'contribution_id': str(feedback_id),
            'points_earned': 10  # Gamification element
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/report-issue', methods=['POST'])
@jwt_required()
def report_issue():
    """Report technical issues or bugs"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        issue_type = data.get('type')  # 'bug', 'performance', 'feature_request', 'accessibility'
        title = data.get('title')
        description = data.get('description')
        severity = data.get('severity', 'medium')  # low, medium, high, critical
        browser_info = data.get('browser_info')
        device_info = data.get('device_info')
        
        if not all([issue_type, title, description]):
            return jsonify({'error': 'Issue type, title, and description are required'}), 400
        
        feedback_data = {
            'type': 'issue',
            'category': issue_type,
            'title': title,
            'comment': description,
            'severity': severity,
            'browser_info': browser_info or request.headers.get('User-Agent'),
            'device_info': device_info
        }
        
        feedback_model = db.get_model('feedback')
        feedback_id = feedback_model.create_feedback(user_id, feedback_data)
        
        # Log analytics event
        analytics_model = db.get_model('analytics')
        analytics_model.log_event(user_id, {
            'event_type': 'issue',
            'event_name': 'report_issue',
            'properties': {
                'issue_type': issue_type,
                'severity': severity,
                'feedback_id': str(feedback_id)
            }
        })
        
        return jsonify({
            'success': True,
            'message': 'Issue reported successfully',
            'issue_id': str(feedback_id),
            'estimated_response_time': '24-48 hours'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/feature-request', methods=['POST'])
@jwt_required()
def submit_feature_request():
    """Submit a feature request"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        title = data.get('title')
        description = data.get('description')
        priority = data.get('priority', 'medium')  # low, medium, high
        use_case = data.get('use_case')
        expected_benefit = data.get('expected_benefit')
        
        if not all([title, description]):
            return jsonify({'error': 'Title and description are required'}), 400
        
        feedback_data = {
            'type': 'feature_request',
            'title': title,
            'comment': description,
            'severity': priority,
            'metadata': {
                'use_case': use_case,
                'expected_benefit': expected_benefit
            },
            'votes': 1,
            'voters': [user_id]
        }
        
        feedback_model = db.get_model('feedback')
        feedback_id = feedback_model.create_feedback(user_id, feedback_data)
        
        # Log analytics event
        analytics_model = db.get_model('analytics')
        analytics_model.log_event(user_id, {
            'event_type': 'feature_request',
            'event_name': 'submit_request',
            'properties': {
                'priority': priority,
                'feedback_id': str(feedback_id)
            }
        })
        
        return jsonify({
            'success': True,
            'message': 'Feature request submitted successfully',
            'request_id': str(feedback_id)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/vote/<request_id>', methods=['POST'])
@jwt_required()
def vote_for_feature(request_id):
    """Vote for a feature request"""
    try:
        user_id = get_jwt_identity()
        
        feedback_model = db.get_model('feedback')
        result = feedback_model.add_vote(request_id, user_id)
        
        if not result:
            return jsonify({'error': 'Feature request not found or already voted'}), 400
        
        # Log analytics event
        analytics_model = db.get_model('analytics')
        analytics_model.log_event(user_id, {
            'event_type': 'feature_request',
            'event_name': 'vote',
            'properties': {
                'feedback_id': request_id
            }
        })
        
        return jsonify({
            'success': True,
            'message': 'Vote recorded successfully',
            'total_votes': result['votes']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
