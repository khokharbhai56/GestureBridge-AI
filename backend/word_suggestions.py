#!/usr/bin/env python3
"""
Word Suggestion Service for GestureBridge AI
Provides intelligent word predictions based on letter sequences
"""

import enchant
from typing import List, Dict, Optional
import json
import os

class WordSuggestionService:
    def __init__(self):
        """Initialize the word suggestion service"""
        try:
            self.dictionary = enchant.Dict("en-US")
            print("✅ Word suggestion service initialized with English dictionary")
        except:
            print("⚠️  Enchant dictionary not available, using fallback")
            self.dictionary = None

        # Load common words for fallback
        self.common_words = self._load_common_words()

        # Word frequency data for better suggestions
        self.word_frequencies = self._load_word_frequencies()

    def _load_common_words(self) -> List[str]:
        """Load common English words for fallback suggestions"""
        common_words = [
            "the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "its", "may", "new", "now", "old", "see", "two", "way", "who", "boy", "did", "has", "let", "put", "say", "she", "too", "use",
            "hello", "thank", "please", "sorry", "yes", "no", "good", "bad", "well", "very", "much", "many", "some", "what", "when", "where", "why", "how", "which", "who", "that", "this", "here", "there",
            "time", "year", "work", "home", "life", "love", "help", "need", "want", "make", "take", "come", "give", "find", "tell", "ask", "work", "seem", "feel", "try", "call", "keep", "begin", "start",
            "school", "class", "student", "teacher", "learn", "study", "read", "write", "book", "paper", "test", "grade", "friend", "family", "parent", "child", "brother", "sister", "mother", "father"
        ]
        return common_words

    def _load_word_frequencies(self) -> Dict[str, int]:
        """Load word frequency data for ranking suggestions"""
        # Simple frequency mapping for common words
        frequencies = {
            "the": 100, "and": 95, "for": 90, "are": 85, "but": 80, "not": 75, "you": 70, "all": 65, "can": 60, "had": 55,
            "hello": 50, "thank": 45, "please": 40, "yes": 35, "no": 30, "good": 25, "what": 20, "how": 15, "when": 10
        }
        return frequencies

    def get_suggestions(self, current_word: str, max_suggestions: int = 5) -> List[str]:
        """
        Get word suggestions based on current word input

        Args:
            current_word: The current word being typed (can be partial)
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggested words
        """
        if not current_word or current_word.strip() == "":
            return []

        current_word = current_word.lower().strip()

        suggestions = []

        # Try enchant dictionary first
        if self.dictionary:
            try:
                # Get suggestions from enchant
                enchant_suggestions = self.dictionary.suggest(current_word)

                # Filter and rank suggestions
                filtered_suggestions = []
                for suggestion in enchant_suggestions[:max_suggestions * 2]:  # Get more for filtering
                    if suggestion.lower().startswith(current_word):
                        filtered_suggestions.append(suggestion)

                # If we have enough prefix matches, use them
                if len(filtered_suggestions) >= max_suggestions:
                    suggestions = filtered_suggestions[:max_suggestions]
                else:
                    # Combine prefix matches with other suggestions
                    suggestions = filtered_suggestions
                    for suggestion in enchant_suggestions:
                        if suggestion.lower() not in [s.lower() for s in suggestions]:
                            suggestions.append(suggestion)
                            if len(suggestions) >= max_suggestions:
                                break

            except Exception as e:
                print(f"Enchant suggestion error: {e}")

        # Fallback to common words if enchant fails or no suggestions
        if len(suggestions) < max_suggestions:
            fallback_suggestions = []
            for word in self.common_words:
                if word.startswith(current_word) and word not in [s.lower() for s in suggestions]:
                    fallback_suggestions.append(word)
                    if len(fallback_suggestions) >= (max_suggestions - len(suggestions)):
                        break

            suggestions.extend(fallback_suggestions)

        # Limit to max_suggestions
        suggestions = suggestions[:max_suggestions]

        # Sort by frequency if available
        suggestions.sort(key=lambda x: self.word_frequencies.get(x.lower(), 0), reverse=True)

        return suggestions

    def get_predictions_from_letters(self, letter_sequence: str, max_predictions: int = 5) -> List[str]:
        """
        Get word predictions based on a sequence of letters

        Args:
            letter_sequence: String of letters (e.g., "hel" for predicting "hello")
            max_predictions: Maximum number of predictions to return

        Returns:
            List of predicted words
        """
        if not letter_sequence or letter_sequence.strip() == "":
            return []

        letter_sequence = letter_sequence.lower().strip()

        # Get suggestions based on the letter sequence
        suggestions = self.get_suggestions(letter_sequence, max_predictions * 2)

        # Filter to only include words that start with the exact sequence
        predictions = []
        for suggestion in suggestions:
            if suggestion.lower().startswith(letter_sequence):
                predictions.append(suggestion)
                if len(predictions) >= max_predictions:
                    break

        # If we don't have enough predictions, try partial matching
        if len(predictions) < max_predictions:
            for word in self.common_words:
                if word.startswith(letter_sequence) and word not in [p.lower() for p in predictions]:
                    predictions.append(word)
                    if len(predictions) >= max_predictions:
                        break

        return predictions[:max_predictions]

    def get_context_aware_suggestions(self, current_word: str, context_words: List[str] = None, max_suggestions: int = 5) -> List[str]:
        """
        Get context-aware word suggestions

        Args:
            current_word: Current word being typed
            context_words: Previous words for context
            max_suggestions: Maximum suggestions to return

        Returns:
            List of context-aware suggestions
        """
        # For now, just return regular suggestions
        # This could be enhanced with NLP models for better context awareness
        return self.get_suggestions(current_word, max_suggestions)

# Global instance
word_suggestion_service = WordSuggestionService()

def get_word_suggestions(current_word: str, max_suggestions: int = 5) -> List[str]:
    """Convenience function to get word suggestions"""
    return word_suggestion_service.get_suggestions(current_word, max_suggestions)

def get_predictions_from_letters(letter_sequence: str, max_predictions: int = 5) -> List[str]:
    """Convenience function to get predictions from letter sequence"""
    return word_suggestion_service.get_predictions_from_letters(letter_sequence, max_predictions)

if __name__ == "__main__":
    # Test the service
    service = WordSuggestionService()

    test_words = ["hel", "th", "wh", "go", "pl"]

    print("🧪 Testing Word Suggestion Service")
    print("=" * 40)

    for word in test_words:
        suggestions = service.get_suggestions(word, 5)
        print(f"Input: '{word}' → Suggestions: {suggestions}")

    print("\n✅ Word suggestion service test completed!")
