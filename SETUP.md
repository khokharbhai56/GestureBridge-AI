# GestureBridge AI - Setup Guide

This guide provides detailed instructions for setting up and running the GestureBridge AI project.

## Quick Start

For those who want to get started immediately, here are the basic commands:

```bash
# Clone and enter project
git clone https://github.com/yourusername/gestureBridge-ai.git
cd gestureBridge-ai

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start MongoDB
sudo systemctl start mongod  # On Windows: Start MongoDB service

# Start the backend
python backend/app.py

# In a new terminal, start the frontend
cd frontend
python -m http.server 8000
```

Visit http://localhost:8000 to access the application.

## Detailed Setup Instructions

### 1. System Requirements

Ensure your system meets these requirements:

- Python 3.8 or higher
- MongoDB 4.4 or higher
- Node.js 14 or higher (for development)
- Git
- Web browser with WebRTC support
- Webcam (for sign language detection)

### 2. MongoDB Setup

1. Install MongoDB:
   ```bash
   # Ubuntu
   sudo apt update
   sudo apt install mongodb

   # macOS with Homebrew
   brew tap mongodb/brew
   brew install mongodb-community

   # Windows
   # Download and install from MongoDB website
   ```

2. Start MongoDB service:
   ```bash
   # Ubuntu/Linux
   sudo systemctl start mongod
   sudo systemctl enable mongod  # Start on boot

   # macOS
   brew services start mongodb-community

   # Windows
   # MongoDB runs as a service automatically
   ```

3. Create database and user:
   ```bash
   mongosh
   > use gesturebridge
   > db.createUser({
       user: "gesturebridgeuser",
       pwd: "your_secure_password",
       roles: ["readWrite"]
   })
   ```

### 3. Python Environment Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate virtual environment:
   ```bash
   # Linux/macOS
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Environment Configuration

1. Create .env file:
   ```bash
   cp .env.example .env
   ```

2. Edit .env with your settings:
   ```env
   # MongoDB Configuration
   MONGO_URI=mongodb://gesturebridgeuser:your_secure_password@localhost:27017/gesturebridge

   # JWT Configuration
   JWT_SECRET_KEY=your-secret-key-change-in-production
   JWT_ACCESS_TOKEN_EXPIRES=3600

   # Server Configuration
   FLASK_APP=backend/app.py
   FLASK_ENV=development
   FLASK_DEBUG=1
   PORT=5000

   # ML Model Configuration
   MODEL_PATH=backend/model/saved_model
   ```

### 5. Initialize Database

1. Run database initialization:
   ```bash
   python backend/database.py
   ```

2. Verify initialization:
   ```bash
   mongosh
   > use gesturebridge
   > show collections
   ```

### 6. Running the Application

1. Start the backend server:
   ```bash
   # From project root
   python backend/app.py
   ```

2. Start the frontend server:
   ```bash
   # From project root, in a new terminal
   cd frontend
   python -m http.server 8000
   ```

3. Access the application:
   - Frontend: http://localhost:8000
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:8000/api-docs.html

### 7. Verify Installation

1. Check MongoDB connection:
   ```bash
   # In Python shell
   from backend.database import db
   db.connect()  # Should return True
   ```

2. Test API endpoints:
   ```bash
   # Using curl
   curl http://localhost:5000/api/health
   # Should return {"status": "healthy", ...}
   ```

3. Test frontend access:
   - Open http://localhost:8000
   - Verify all static assets load
   - Check browser console for errors

### 8. Common Issues and Solutions

1. MongoDB Connection Issues:
   ```bash
   # Check MongoDB status
   sudo systemctl status mongod

   # Check MongoDB logs
   sudo tail -f /var/log/mongodb/mongod.log

   # Verify connection string
   mongosh "mongodb://gesturebridgeuser:your_password@localhost:27017/gesturebridge"
   ```

2. Port Conflicts:
   ```bash
   # Check if ports are in use
   sudo lsof -i :5000
   sudo lsof -i :8000

   # Kill processes if needed
   kill -9 <PID>
   ```

3. Python Virtual Environment:
   ```bash
   # Recreate virtual environment if needed
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### 9. Development Setup

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. Configure IDE:
   - VSCode: Install Python and MongoDB extensions
   - PyCharm: Configure Python interpreter from venv

### 10. Testing

1. Run tests:
   ```bash
   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_auth.py

   # Run with coverage
   pytest --cov=backend tests/
   ```

2. Generate coverage report:
   ```bash
   coverage html
   # Open htmlcov/index.html in browser
   ```

### 11. Updating

1. Update repository:
   ```bash
   git pull origin main
   ```

2. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. Apply database migrations:
   ```bash
   python backend/database.py --migrate
   ```

### 12. Maintenance

1. Database backup:
   ```bash
   mongodump --db gesturebridge --out backup/
   ```

2. Log rotation:
   ```bash
   # Check logs
   tail -f logs/app.log

   # Rotate logs
   logrotate config/logrotate.conf
   ```

3. Clear cache:
   ```bash
   # Remove cached files
   rm -rf backend/__pycache__
   rm -rf frontend/cache/*
   ```

For additional help:
- Check the [README.md](README.md) for project overview
- Visit the [Help Center](http://localhost:8000/help-center.html)
- Submit issues on GitHub
- Contact support@gesturebridge.ai
