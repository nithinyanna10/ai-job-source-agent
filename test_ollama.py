"""
Quick test to verify Ollama is working with your model
"""

import requests
import json

def test_ollama():
    """Test Ollama connection and model"""
    ollama_url = "http://localhost:11434"
    model = "gpt-oss:120b-cloud"
    
    print("=" * 60)
    print("Testing Ollama Connection")
    print("=" * 60)
    
    # Test 1: Check if Ollama is running
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama is running")
            print(f"📦 Available models: {[m.get('name') for m in models]}")
            
            # Check if our model is available
            model_names = [m.get('name') for m in models]
            if model in model_names:
                print(f"✅ Model '{model}' is available")
            else:
                print(f"⚠️  Model '{model}' not found in available models")
                print(f"   Available: {model_names}")
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Test chat API
    print("\n" + "=" * 60)
    print("Testing Chat API")
    print("=" * 60)
    
    try:
        chat_url = f"{ollama_url}/api/chat"
        prompt = "Which link is most likely a careers page: /about, /careers, /contact, /blog"
        
        print(f"📤 Sending prompt to model '{model}'...")
        response = requests.post(chat_url, json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("message", {}).get("content", "")
            print(f"✅ Model responded:")
            print(f"   {answer}")
            return True
        else:
            print(f"❌ Chat API returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chat: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    print("\n" + "=" * 60)
    if success:
        print("✅ Ollama is ready to use!")
    else:
        print("❌ Ollama test failed. Check your setup.")
    print("=" * 60)

