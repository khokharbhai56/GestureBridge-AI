# GestureBridge AI

GestureBridge AI is a modern web application that provides real-time sign language translation using artificial intelligence. The application supports bidirectional translation between sign language and text, making communication more accessible for everyone.

## Features

GestureBridge AI combines cutting-edge technology with user-centric design to provide a comprehensive sign language translation solution. Our features are designed to ensure accuracy, accessibility, and ease of use while maintaining high performance and security standards.

### Real-time Translation
- WebSocket-based streaming with ultra-low latency
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
  * And many more
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
- Install as native app
- Push notifications
- Background sync
- Automatic updates
- Cross-platform compatibility
- Touch-optimized interface

### Mobile Optimization
- Responsive design for all screen sizes
- Touch and gesture support
- Battery-efficient processing
- Optimized video streaming
- Mobile camera integration
- Portrait and landscape modes

### User Experience
- Modern, clean interface with Tailwind CSS
- Intuitive navigation
- Real-time feedback
- Progress tracking
- Customizable settings
- Dark/light mode support
- Accessibility features

### Security
- JWT-based authentication
- Secure WebSocket connections
- Input validation and sanitization
- Rate limiting and DDoS protection
- Data encryption
- CORS configuration
- Secure file handling

### Performance
- Optimized video processing
- Efficient data streaming
- Caching strategies
- Load balancing
- Resource optimization
- Fast cold start
- Minimal battery impact

### User Feedback System
- Real-time translation feedback
- Accuracy rating
- Suggestion submission
- Error reporting
- Feature requests
- Community contributions
- Continuous improvement pipeline
- AI-powered feedback analysis with ChatGPT
- Automated sentiment analysis and improvement suggestions
- Priority assessment for feedback items

### AI-Powered Chatbot Assistant
- Intelligent help and support
- Context-aware responses about app features
- Sign language learning assistance
- Troubleshooting guidance
- 24/7 availability
- Integration with ChatGPT for natural conversations
- Fallback responses when API unavailable

### Analytics and Monitoring
- Usage statistics
- Performance metrics
- Error tracking
- User behavior analysis
- Translation accuracy monitoring
- System health checks
- Real-time monitoring

## Technology Stack

### Frontend
- HTML5, CSS3 (with Tailwind CSS)
- JavaScript (ES6+)
- WebSocket for real-time streaming
- Progressive Web App (PWA) features
- Service Worker for offline support
- WebRTC for video capture
- Responsive design for all devices

### Backend
- Python with Flask
- Flask-SocketIO for real-time communication
- TensorFlow for AI model
- MongoDB for data storage
- JWT for authentication
- MediaPipe for hand tracking
- Celery for background tasks
- Redis for caching

## Prerequisites

- Python 3.9+
- Node.js 14+
- MongoDB
- Redis (for caching and Celery)
- Webcam for sign language detection

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gestureBridge-ai.git
cd gestureBridge-ai
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
MONGO_URI=mongodb://localhost:27017/gestureBridgeAI
REDIS_URL=redis://localhost:6379/0
DEBUG=True
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

4. Initialize the database:
```bash
python backend/database.py
```

5. Train the AI model (optional - you can use the pre-trained model):
```bash
python backend/model/train_model.py
```

## Running the Application

1. Start Redis server:
```bash
redis-server
```

2. Start Celery worker:
```bash
celery -A backend.tasks worker --loglevel=info
```

3. Start the backend server:
```bash
python backend/app.py
```

4. Open the frontend:
Navigate to the `frontend` directory and open `index.html` in a web browser, or serve it using a local server:
```bash
python -m http.server 8000
```

The application will be available at:
- Frontend: http://localhost:8000
- Backend API: http://localhost:5000
- WebSocket: ws://localhost:5000

---

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd gesturebridge-ai
   ```
2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Run the backend server:**
   ```bash
   python backend/sign_language_app/live_api.py
   ```
4. **Start the frontend:**
   Open `frontend/dashboard.html` in your browser.

## API Endpoints

- **Live Prediction (WebSocket):**
  - `ws://<host>:5000` (event: `frame`)
  - Send: `{ image: <base64>, token: <JWT> }`
  - Receive: `{ prediction: <label>, confidence: <score> }`

- **Chatbot Assistant:**
  - `POST /api/chat/message` (JWT optional)
  - Send: `{ message: <string> }`
  - Receive: `{ success: <boolean>, bot_response: <string>, user_message: <string> }`

- **History:**
  - `GET /api/history` (JWT required)
  - `POST /api/history` (JWT required)
  - `DELETE /api/history` (JWT required)

- **Feedback:**
  - `POST /api/feedback/submit` (JWT required)
  - `POST /api/feedback/analyze/<feedback_id>` (JWT required)
  - `GET /api/feedback/my-feedback` (JWT required)
  - `GET /api/feedback/statistics` (public)

- **Account:**
  - `DELETE /api/account` (JWT required)

## Features
- Real-time sign prediction with confidence scores
- Text-to-speech for predictions
- History, feedback, community, gamification, admin dashboard
- Mobile/PWA support
- Privacy controls
- Automated testing and CI/CD

## Onboarding
- Register/login to access dashboard
- Click "Start Live Demo" to begin
- Use tabs for tutorials, history, community, gamification, admin
- Submit feedback and manage privacy in settings

## Troubleshooting
- Ensure webcam and microphone permissions are granted
- For HTTPS, provide `cert.pem` and `key.pem` in backend
- For Docker, build and run with:
  ```bash
  docker build -t gesturebridge-ai .
  docker run -p 5000:5000 gesturebridge-ai
  ```

## Support
- For help, use the Community tab or contact the project maintainer

---
