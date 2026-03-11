#!/usr/bin/env python3
"""
Quick test to verify OpenAI integration works
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai():
    """Test OpenAI integration"""
    print("\n" + "="*60)
    print("Testing OpenAI Integration")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    # Test import
    try:
        from agents.openai_integration import OpenAIAssistant
        print("✅ OpenAI integration module imported")
    except Exception as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    # Test initialization
    try:
        assistant = OpenAIAssistant("test_user")
        print(f"✅ Assistant initialized")
        print(f"   Model: {assistant.model if hasattr(assistant, 'model') else 'N/A'}")
        print(f"   Client: {'Connected' if assistant.client else 'Mock mode'}")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Test 1: Parse natural language request
    print("\n📝 Test 1: Parsing natural language request")
    print("   Input: 'Schedule 30-min sync with Sarah next week, afternoon'")
    
    try:
        result = await assistant.parse_natural_language_request(
            "Schedule 30-min sync with Sarah next week, afternoon"
        )
        print(f"✅ Parsed successfully!")
        print(f"   Result: {result}")
        
        # Validate result
        if isinstance(result, dict):
            print(f"   ✓ Attendees: {result.get('attendees', [])}")
            print(f"   ✓ Duration: {result.get('duration', 'N/A')} minutes")
            print(f"   ✓ Time preference: {result.get('time_preference', 'N/A')}")
            print(f"   ✓ Priority: {result.get('priority', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Generate explanation
    print("\n💬 Test 2: Generating explanation")
    
    try:
        from datetime import datetime, timedelta
        
        explanation = await assistant.generate_explanation(
            recommendation={
                "start_time": datetime.now() + timedelta(days=2),
                "end_time": datetime.now() + timedelta(days=2, hours=1),
                "confidence": 0.92
            },
            context={
                "type": "team_sync",
                "priority": "medium",
                "attendees": ["Sarah", "Marcus"]
            }
        )
        
        print(f"✅ Explanation generated!")
        print(f"   {explanation[:200]}...")
        
    except Exception as e:
        print(f"❌ Explanation generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("🎉 All OpenAI tests passed!")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_openai())
    exit(0 if success else 1)
