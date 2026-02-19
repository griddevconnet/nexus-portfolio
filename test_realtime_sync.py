#!/usr/bin/env python3
"""
Test real-time message syncing between client chat and developer dashboard
"""
import requests
import time
import json

def test_message_sync():
    print("🔄 Testing Real-Time Message Sync")
    print("=" * 50)
    
    # Step 1: Send a message from client
    print("📤 Step 1: Sending message from client...")
    
    client_message = {
        "client_name": "Test User",
        "client_email": "test@example.com", 
        "message": "Hello from client! This should appear in developer dashboard.",
        "tag": "greeting"
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/api/chat/start_conversation/",
        json=client_message,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        data = response.json()
        conv_id = data.get('conversation_id')
        print(f"✅ Message sent! Conversation ID: {conv_id}")
        
        # Step 2: Check if message appears in developer dashboard
        print("\n📥 Step 2: Checking developer dashboard...")
        
        # Wait a moment for processing
        time.sleep(2)
        
        # Get conversations from developer API (requires authentication)
        auth_response = requests.post(
            "http://127.0.0.1:8000/api/chat/auth/authenticate/",
            json={"passphrase": "nexus2025"}
        )
        
        if auth_response.status_code == 200:
            cookies = auth_response.cookies
            
            # Get messages for this conversation
            msg_response = requests.get(
                f"http://127.0.0.1:8000/api/chat/messages/?conversation_id={conv_id}",
                cookies=cookies
            )
            
            if msg_response.status_code == 200:
                messages = msg_response.json()
                print(f"✅ Found {len(messages)} messages in conversation")
                
                # Look for our test message
                test_msg_found = False
                for msg in messages:
                    content = msg.get('content', '') if isinstance(msg, dict) else str(msg)
                    if "Hello from client!" in content:
                        print(f"🎯 TEST MESSAGE FOUND: {content}")
                        test_msg_found = True
                        break
                
                if test_msg_found:
                    print("\n🎉 REAL-TIME SYNC WORKING!")
                    print("   Client message successfully appeared in developer dashboard")
                else:
                    print("\n⚠️  TEST MESSAGE NOT FOUND")
                    print("   Check message polling in developer dashboard")
            else:
                print(f"❌ Failed to get messages: {msg_response.status_code}")
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
    else:
        print(f"❌ Failed to send message: {response.status_code}")

if __name__ == "__main__":
    test_message_sync()
