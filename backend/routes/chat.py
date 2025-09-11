from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

# Fix import error by adding backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from config import Config
import openai

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/message', methods=['POST'])
# @jwt_required()  # Temporarily disabled for testing
def send_message():
    """Send a message to the AI chatbot"""
    try:
        # user_id = get_jwt_identity()  # Temporarily disabled
        data = request.get_json()

        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Get chatbot response
        bot_response = get_chatbot_response(user_message)

        # Log the conversation (optional)
        # You can add database logging here if needed

        return jsonify({
            'success': True,
            'user_message': user_message,
            'bot_response': bot_response
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_chatbot_response(message):
    """
    Get response from ChatGPT for user assistance
    """
    try:
        if not Config.OPENAI_API_KEY:
            # Enhanced fallback responses with comprehensive knowledge
            message_lower = message.lower()

            # Greeting responses
            if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
                return "Hello! Welcome to GestureBridge AI! I'm here to help you with sign language translation, app features, troubleshooting, or any questions about our platform. How can I assist you today?"

            # Help and general questions
            if any(word in message_lower for word in ['help', 'support', 'assist', 'guide']):
                return "I'd be happy to help! I can assist you with:\n\n• Getting started with GestureBridge AI\n• Understanding sign language basics\n• Troubleshooting technical issues\n• Account management\n• API documentation\n• Community features\n\nWhat specific area would you like help with?"

            # How to use questions
            if any(word in message_lower for word in ['how', 'use', 'start', 'begin', 'tutorial']):
                return "To get started with GestureBridge AI:\n\n1. Register or login to your account\n2. Grant camera and microphone permissions\n3. Click 'Start Live Demo' on your dashboard\n4. Select your preferred sign language\n5. Position yourself 2-3 feet from the camera\n6. Begin signing naturally!\n\nFor detailed tutorials, visit our Help Center at /help-center.html"

            # What is questions
            if any(word in message_lower for word in ['what', 'about', 'features', 'capabilities']):
                return "GestureBridge AI is a comprehensive sign language translation platform featuring:\n\n• Real-time translation with <100ms latency\n• 15+ international sign languages (ASL, BSL, JSL, etc.)\n• 99.2% accuracy with AI-powered recognition\n• Progressive Web App with offline support\n• Mobile-optimized interface\n• Community forums and feedback system\n\nWould you like to know more about any specific feature?"

            # Sign language questions
            if any(word in message_lower for word in ['sign language', 'asl', 'bsl', 'sign', 'gesture']):
                return "GestureBridge AI supports multiple sign languages including ASL, BSL, JSL, LSF, DGS, and many regional variants. For best results:\n\n• Use clear, crisp handshapes\n• Include appropriate facial expressions\n• Sign at a natural pace\n• Ensure good lighting and plain background\n• Position 2-3 feet from camera\n\nWould you like tips for a specific sign language?"

            # Troubleshooting questions
            if any(word in message_lower for word in ['problem', 'issue', 'error', 'trouble', 'not working']):
                return "I'm sorry you're experiencing issues! Common solutions include:\n\n• Check camera/microphone permissions in your browser\n• Ensure good lighting and reduce background clutter\n• Try a different browser (Chrome, Firefox, Safari, Edge)\n• Clear browser cache and refresh the page\n• Check your internet connection (5 Mbps minimum)\n\nFor specific error messages, please share more details so I can help troubleshoot."

            # Account questions
            if any(word in message_lower for word in ['account', 'login', 'register', 'password', 'profile']):
                return "For account-related help:\n\n• Register: Visit /register to create a new account\n• Login: Use /login with your credentials\n• Password Reset: Click 'Forgot Password' on login page\n• Profile: Update settings in your dashboard\n• Security: Enable 2FA in account settings\n\nNeed help with a specific account issue?"

            # API questions
            if any(word in message_lower for word in ['api', 'developer', 'integration', 'documentation']):
                return "For API documentation and developer resources:\n\n• API Docs: Visit /api-docs.html for complete documentation\n• Authentication: JWT-based with Bearer tokens\n• Endpoints: Available for streaming, feedback, history, etc.\n• WebSocket: Real-time translation at ws://host:port/streaming\n• SDKs: REST API with JSON responses\n\nCheck our API documentation for code examples and integration guides."

            # Community questions
            if any(word in message_lower for word in ['community', 'forum', 'discuss', 'share']):
                return "Join our vibrant community at /community.html where you can:\n\n• Share your experiences with sign language translation\n• Ask questions and get help from other users\n• Participate in discussions and workshops\n• Contribute to improving the platform\n• Connect with the deaf and hard-of-hearing community\n\nThe community is a great place to learn and share!"

            # Contact questions
            if any(word in message_lower for word in ['contact', 'support', 'email', 'reach']):
                return "You can reach us through several channels:\n\n• Support: support@gesturebridge.ai (24-48 hour response)\n• Business: business@gesturebridge.ai\n• Technical: dev@gesturebridge.ai\n• General: info@gesturebridge.ai\n• Contact Form: /contact.html\n\nWe're here to help with any questions or concerns!"

            # Default response
            return "I'm your GestureBridge AI assistant with comprehensive knowledge about our platform! I can help you with:\n\n• Getting started and tutorials\n• Sign language basics and best practices\n• Troubleshooting technical issues\n• Account management and settings\n• API documentation and integration\n• Community features and forums\n• Contact information and support\n\nWhat would you like to know about GestureBridge AI?"

        openai.api_key = Config.OPENAI_API_KEY

        system_prompt = """You are an expert AI assistant for GestureBridge AI, a comprehensive sign language translation platform. You have complete knowledge of the website, features, sign languages, and all aspects of the application.

## WEBSITE OVERVIEW
GestureBridge AI is a modern web application that provides real-time sign language translation using artificial intelligence. It supports bidirectional translation between sign language and text, making communication more accessible for everyone.

## SUPPORTED FEATURES
### Real-time Translation
- WebSocket-based streaming with ultra-low latency (<100ms)
- Frame-by-frame processing with instant feedback
- Multi-person detection and translation
- Background noise filtering and gesture isolation
- Continuous streaming with automatic reconnection
- Video quality adaptation based on network conditions

### Language Support
- 15+ international sign languages including:
  * American Sign Language (ASL)
  * British Sign Language (BSL)
  * Japanese Sign Language (JSL)
  * French Sign Language (LSF)
  * German Sign Language (DGS)
  * Spanish Sign Language (LSE)
  * Italian Sign Language (LIS)
  * And many more regional variants
- Regional dialect detection and adaptation
- Cultural context awareness
- Automatic language detection
- Cross-language translation support

### AI and Machine Learning
- Enhanced AI model with 99.2% accuracy
- Real-time learning from user feedback
- Context-aware translation
- Emotion and sentiment detection
- Gesture prediction and suggestions
- Continuous model improvement
- Multi-modal recognition (gestures, facial expressions, body language)

### Progressive Web App
- Offline functionality with service worker
- Install as native app on mobile/desktop
- Push notifications for updates
- Background sync for offline data
- Automatic updates
- Cross-platform compatibility
- Touch-optimized interface

### Mobile Optimization
- Responsive design for all screen sizes (320px to 4K)
- Touch and gesture support
- Battery-efficient processing (optimized for 2+ hours continuous use)
- Optimized video streaming (H.264/WebRTC)
- Mobile camera integration (front/back camera support)
- Portrait and landscape modes

## HOW TO USE THE APP
### Getting Started
1. Register/Login: Create account at /register or login at /login
2. Grant Permissions: Allow camera and microphone access
3. Start Demo: Click "Start Live Demo" on dashboard
4. Select Language: Choose from supported sign languages
5. Begin Translation: Make signs in front of camera

### Navigation
- Home (/): Main landing page with feature overview
- Dashboard: Personal translation workspace
- Help Center (/help-center.html): Tutorials and support
- API Docs (/api-docs.html): Developer documentation
- Community (/community.html): User forums and discussions
- Contact (/contact.html): Support contact form

## SIGN LANGUAGE BASICS
### ASL Fundamentals
- Alphabet: 26 letters with distinct handshapes
- Numbers: 0-9 with unique signs
- Common phrases: Hello, Thank you, Please, Sorry, etc.
- Facial expressions: Critical for meaning (questions, statements, emotions)
- Body language: Posture and movement add context

### Best Practices
- Clear handshapes: Keep signs crisp and defined
- Facial expressions: Use appropriate facial grammar
- Lighting: Well-lit environment, avoid backlighting
- Background: Plain background for better detection
- Distance: 2-3 feet from camera
- Speed: Natural signing pace (not too fast/slow)

## TROUBLESHOOTING
### Common Issues
1. Camera not detected: Check browser permissions, try different browser
2. Poor accuracy: Improve lighting, reduce background clutter, slower signing
3. Audio issues: Check microphone permissions, test audio settings
4. Connection problems: Check internet, try refreshing page
5. Mobile issues: Update browser, check battery optimization settings

### Technical Requirements
- Modern browser: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Camera: 720p minimum, 1080p recommended
- Internet: 5 Mbps minimum for streaming
- RAM: 4GB minimum, 8GB recommended
- Storage: 500MB for app, additional for offline data

## ACCOUNT MANAGEMENT
- Profile: Update personal information, language preferences
- Security: Change password, enable 2FA
- Privacy: Control data sharing, manage stored translations
- Billing: Subscription management (if applicable)
- History: View past translations, export data

## API DOCUMENTATION
### Authentication
- JWT-based authentication
- Bearer token in Authorization header
- Token refresh mechanism

### Endpoints
- POST /api/auth/login: User authentication
- POST /api/auth/register: User registration
- POST /api/streaming/start: Start translation session
- POST /api/streaming/process_frame: Process video frame
- POST /api/feedback/submit: Submit user feedback
- GET /api/history: Retrieve translation history

### WebSocket
- ws://host:port/streaming: Real-time translation
- Message format: {frame: base64_image, session_id: string}
- Response: {translation: string, confidence: float}

## COMMUNITY FEATURES
- User forums: Share experiences, ask questions
- Feedback system: Rate translations, suggest improvements
- Leaderboards: Top contributors, accuracy rankings
- Tutorials: User-generated learning content
- Events: Virtual meetups, workshops

## SECURITY & PRIVACY
- End-to-end encryption for all communications
- GDPR compliant data handling
- No permanent storage of video data
- User-controlled data retention
- Regular security audits
- SOC 2 Type II certified infrastructure

## CONTACT INFORMATION
- Support Email: support@gesturebridge.ai
- Business Inquiries: business@gesturebridge.ai
- Technical Issues: dev@gesturebridge.ai
- General: info@gesturebridge.ai
- Response Time: 24-48 hours for support tickets

## RESPONSE GUIDELINES
- Be friendly, patient, and encouraging
- Provide step-by-step instructions when explaining features
- Include relevant links to documentation when appropriate
- Admit limitations if you don't have specific information
- Encourage user feedback and community participation
- Use simple language, avoid technical jargon unless necessary
- Always offer to help with next steps or related questions

Remember: You are the primary interface for users learning about and using GestureBridge AI. Your knowledge should be comprehensive and your responses should build user confidence and success with the platform."""

        response = openai.ChatCompletion.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=300,
            temperature=0.7
        )

        bot_response = response.choices[0].message.content.strip()
        return bot_response

    except Exception as e:
        print(f"Error getting chatbot response: {e}")
        return "I'm sorry, I'm having trouble responding right now. Please try again later or check our help documentation."
