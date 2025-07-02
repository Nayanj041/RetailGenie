#!/usr/bin/env python3
"""
Test script for Google Gemini integration in RetailGenie
"""

import os
import sys
sys.path.append('.')

def test_gemini_integration():
    """Test Google Gemini integration"""
    print("🧪 Testing Google Gemini Integration...")
    
    try:
        # Test import
        import google.generativeai as genai
        print("✅ Google Generative AI library imported successfully")
        
        # Test API key configuration
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            print("✅ Gemini API key found in environment")
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Create model
            model = genai.GenerativeModel("gemini-pro")
            print("✅ Gemini model created successfully")
            
            # Test simple generation
            try:
                response = model.generate_content("Hello! Say 'Gemini is working' if you can read this.")
                print(f"✅ Gemini response: {response.text}")
                return True
            except Exception as e:
                print(f"⚠️  Gemini API call failed: {str(e)}")
                print("   (This is expected if API key is not valid)")
                return False
        else:
            print("⚠️  Gemini API key not found in environment")
            print("   Set GEMINI_API_KEY in your .env file")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import Google Generative AI: {str(e)}")
        print("   Run: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_ai_controller():
    """Test AI Controller with Gemini"""
    print("\n🧪 Testing AI Controller with Gemini...")
    
    try:
        from app.controllers.ai_assistant_controller import AIAssistantController
        
        controller = AIAssistantController()
        print("✅ AI Assistant Controller created successfully")
        
        if controller.gemini_model:
            print("✅ Gemini model configured in controller")
        else:
            print("⚠️  Gemini model not configured (API key missing)")
        
        # Test a simple chat message
        response = controller.process_chat_message(
            "Hello, can you help me find products?",
            "test-user"
        )
        
        print(f"✅ Chat response generated: {response.get('text', 'No text')[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ AI Controller test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 RetailGenie Gemini Integration Test\n")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = True
    
    # Test Gemini integration
    success &= test_gemini_integration()
    
    # Test AI controller
    success &= test_ai_controller()
    
    print("\n" + "="*50)
    if success:
        print("🎉 All tests passed! Gemini integration is working.")
    else:
        print("⚠️  Some tests failed. Check configuration and API key.")
    print("="*50)
