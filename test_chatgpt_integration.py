#!/usr/bin/env python3
"""
Test script for ChatGPT integration in GestureBridge AI
Tests both the chat functionality and translation refinement
"""

import requests
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_chat_endpoint():
    """Test the chat endpoint"""
    print("🧪 Testing Chat Endpoint...")

    url = "http://localhost:5000/api/chat/message"
    test_messages = [
        "Hello, can you help me?",
        "How do I use GestureBridge AI?",
        "What languages do you support?",
        "I'm having trouble with my camera"
    ]

    for message in test_messages:
        print(f"\n📤 Sending: {message}")
        try:
            response = requests.post(url, json={"message": message}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data.get('bot_response', 'No response')[:100]}...")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

def test_translation_refinement():
    """Test translation refinement (requires JWT token)"""
    print("\n🧪 Testing Translation Refinement...")

    # This would require a valid JWT token, so we'll just test the basic functionality
    print("ℹ️  Translation refinement requires authentication. Testing basic functionality...")

    # Test without authentication to see error handling
    url = "http://localhost:5000/api/streaming/start"
    try:
        response = requests.post(url, json={"language": "ASL", "quality": "medium"}, timeout=5)
        if response.status_code == 401:
            print("✅ Authentication properly required for streaming endpoints")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_health_check():
    """Test if the server is running"""
    print("\n🧪 Testing Server Health...")

    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding")
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("💡 Make sure to run: python backend/app.py")

def main():
    """Run all tests"""
    print("🚀 GestureBridge AI ChatGPT Integration Test Suite")
    print("=" * 50)

    test_health_check()
    test_chat_endpoint()
    test_translation_refinement()

    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\n📝 Next Steps:")
    print("1. Set OPENAI_API_KEY in your environment variables for full functionality")
    print("2. Test the frontend chat interface at /help-center.html")
    print("3. Test streaming features with proper authentication")

if __name__ == "__main__":
    main()
