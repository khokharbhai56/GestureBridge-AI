from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

# Fix import error by adding backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from word_suggestions import get_word_suggestions, get_predictions_from_letters

suggestions_bp = Blueprint('suggestions', __name__)

@suggestions_bp.route('/word', methods=['POST'])
@jwt_required()
def get_word_suggestions_endpoint():
    """Get word suggestions based on current word input"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        current_word = data.get('current_word', '').strip()
        max_suggestions = min(int(data.get('max_suggestions', 5)), 10)  # Max 10 suggestions

        if not current_word:
            return jsonify({
                'success': True,
                'suggestions': [],
                'message': 'No word provided'
            })

        # Get word suggestions
        suggestions = get_word_suggestions(current_word, max_suggestions)

        return jsonify({
            'success': True,
            'current_word': current_word,
            'suggestions': suggestions,
            'count': len(suggestions)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'suggestions': []
        }), 500

@suggestions_bp.route('/letters', methods=['POST'])
@jwt_required()
def get_letter_predictions_endpoint():
    """Get word predictions based on letter sequence"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        letter_sequence = data.get('letter_sequence', '').strip()
        max_predictions = min(int(data.get('max_predictions', 5)), 10)  # Max 10 predictions

        if not letter_sequence:
            return jsonify({
                'success': True,
                'predictions': [],
                'message': 'No letter sequence provided'
            })

        # Get predictions from letter sequence
        predictions = get_predictions_from_letters(letter_sequence, max_predictions)

        return jsonify({
            'success': True,
            'letter_sequence': letter_sequence,
            'predictions': predictions,
            'count': len(predictions)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'predictions': []
        }), 500

@suggestions_bp.route('/context', methods=['POST'])
@jwt_required()
def get_context_suggestions_endpoint():
    """Get context-aware word suggestions"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        current_word = data.get('current_word', '').strip()
        context_words = data.get('context_words', [])
        max_suggestions = min(int(data.get('max_suggestions', 5)), 10)

        if not current_word:
            return jsonify({
                'success': True,
                'suggestions': [],
                'message': 'No word provided'
            })

        # For now, use basic suggestions (can be enhanced with NLP context)
        from word_suggestions import word_suggestion_service
        suggestions = word_suggestion_service.get_context_aware_suggestions(
            current_word, context_words, max_suggestions
        )

        return jsonify({
            'success': True,
            'current_word': current_word,
            'context_words': context_words,
            'suggestions': suggestions,
            'count': len(suggestions)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'suggestions': []
        }), 500

@suggestions_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_suggestion_stats():
    """Get statistics about the suggestion service"""
    try:
        user_id = get_jwt_identity()

        # Basic stats (can be enhanced with actual usage tracking)
        stats = {
            'service_status': 'active',
            'supported_languages': ['en-US'],
            'max_suggestions': 10,
            'features': [
                'word_completion',
                'spell_checking',
                'letter_sequence_prediction',
                'context_aware_suggestions'
            ]
        }

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
