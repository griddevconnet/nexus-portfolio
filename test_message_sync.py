#!/usr/bin/env python3
"""
Test script to verify message syncing between frontend and backend
"""
import requests
import json

# Test the new authentication endpoint
def test_auth():
    print("🔐 Testing developer authentication...")
    auth_url = "http://127.0.0.1:8000/api/chat/auth/authenticate/"
    
    response = requests.post(auth_url, json={"passphrase": "nexus2025"})
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Authentication successful!")
            print(f"   User: {data['user']['username']}")
            return response.cookies  # Return session cookies
        else:
            print(f"❌ Authentication failed: {data.get('message')}")
            return None
    else:
        print(f"❌ Auth request failed: {response.status_code}")
        return None

# Test conversations endpoint with session
def test_conversations(cookies):
    print("\n📝 Testing conversations endpoint...")
    conv_url = "http://127.0.0.1:8000/api/chat/conversations/"
    
    response = requests.get(conv_url, cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Conversations loaded! Count: {len(data)}")
        return True
    else:
        print(f"❌ Conversations request failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

# Test templates endpoint with session
def test_templates(cookies):
    print("\n📋 Testing templates endpoint...")
    tmpl_url = "http://127.0.0.1:8000/api/chat/templates/"
    
    response = requests.get(tmpl_url, cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Templates loaded! Count: {len(data)}")
        return True
    else:
        print(f"❌ Templates request failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Nexus Message Sync System")
    print("=" * 50)
    
    # Test authentication
    cookies = test_auth()
    
    if cookies:
        # Test API endpoints
        conv_ok = test_conversations(cookies)
        tmpl_ok = test_templates(cookies)
        
        print("\n📊 SUMMARY:")
        print(f"   Authentication: ✅")
        print(f"   Conversations API: {'✅' if conv_ok else '❌'}")
        print(f"   Templates API: {'✅' if tmpl_ok else '❌'}")
        
        if conv_ok and tmpl_ok:
            print("\n🎉 Message syncing is ready!")
        else:
            print("\n⚠️  Some endpoints need attention")
    else:
        print("\n❌ Cannot test APIs - authentication failed")
