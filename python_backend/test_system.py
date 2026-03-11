#!/usr/bin/env python3
"""
Quick test script for the AI scheduling system
Tests each component independently
"""

import asyncio
import os
from datetime import datetime, timedelta


async def test_openai_integration():
    """Test OpenAI API integration"""
    print("\n" + "="*60)
    print("TEST 1: OpenAI Integration")
    print("="*60)
    
    from agents.openai_integration import OpenAIAssistant
    
    assistant = OpenAIAssistant("test_user")
    
    # Test 1: Parse natural language
    print("\n📝 Parsing: 'Schedule 30-min sync with Sarah next week, afternoon'")
    result = await assistant.parse_natural_language_request(
        "Schedule 30-min sync with Sarah next week, afternoon"
    )
    print(f"✅ Parsed: {result}")
    
    # Test 2: Generate explanation
    print("\n💬 Generating explanation...")
    explanation = await assistant.generate_explanation(
        recommendation={
            "start_time": datetime.now() + timedelta(days=2),
            "confidence": 0.92
        },
        context={"type": "team_sync", "priority": "medium"}
    )
    print(f"✅ Explanation: {explanation[:100]}...")
    
    return True


async def test_ml_behavior_model():
    """Test ML behavior learning"""
    print("\n" + "="*60)
    print("TEST 2: ML Behavior Model")
    print("="*60)
    
    from agents.ml_behavior_model import BehaviorLearningModel
    
    model = BehaviorLearningModel("test_user")
    
    # Create sample historical data
    historical_data = []
    for i in range(50):
        historical_data.append({
            "meeting_id": f"m{i}",
            "start_time": datetime.now() - timedelta(days=i),
            "duration": 60,
            "type": "team_sync" if i % 2 == 0 else "one_on_one",
            "priority": "medium",
            "was_accepted": i % 3 != 0,  # 66% acceptance
            "was_rescheduled": i % 5 == 0,  # 20% reschedule
            "response_time": 120
        })
    
    print(f"\n📊 Training on {len(historical_data)} historical meetings...")
    model.train(historical_data)
    
    # Test prediction
    test_window = {
        "start": datetime.now() + timedelta(days=1, hours=14),
        "end": datetime.now() + timedelta(days=1, hours=15)
    }
    
    acceptance_prob = model.predict_acceptance(
        test_window,
        {"type": "team_sync", "priority": "medium"},
        historical_data
    )
    
    print(f"✅ Acceptance probability: {acceptance_prob:.2%}")
    print(f"✅ Learned patterns: {model.get_learned_patterns()}")
    
    return True


async def test_personal_agent():
    """Test personal agent (without database)"""
    print("\n" + "="*60)
    print("TEST 3: Personal Agent")
    print("="*60)
    
    from agents.personal_agent import PersonalAgent
    
    agent = PersonalAgent("test_user")
    
    # Mock data (since we may not have DB)
    agent.private_calendar = []
    agent.private_preferences = {
        "work_hours_start": "09:00",
        "work_hours_end": "17:00",
        "preferred_meeting_duration": 30
    }
    agent.historical_data = []
    
    print("\n🤖 Executing personal agent...")
    result = await agent.execute({
        "request_type": "availability_check",
        "time_windows": [{
            "start": datetime.now() + timedelta(days=1, hours=14),
            "end": datetime.now() + timedelta(days=1, hours=15)
        }],
        "meeting_context": {"type": "team_sync", "priority": "medium"}
    })
    
    print(f"✅ Status: {result.status}")
    print(f"✅ Confidence: {result.confidence:.2%}")
    print(f"✅ Signals: {len(result.data.get('availability_signals', []))}")
    
    return True


async def test_langgraph_orchestrator():
    """Test LangGraph orchestrator"""
    print("\n" + "="*60)
    print("TEST 4: LangGraph Orchestrator")
    print("="*60)
    
    from agents.langgraph_orchestrator import LangGraphOrchestrator
    
    orchestrator = LangGraphOrchestrator()
    
    print("\n🎯 Executing workflow...")
    print("Request: 'Schedule team sync next week'")
    print("Attendees: ['u1', 'u2']")
    
    try:
        result = await orchestrator.execute(
            request="Schedule team sync next week",
            attendee_ids=["u1", "u2"],
            duration=30,
            meeting_context={"type": "team_sync", "priority": "medium"}
        )
        
        print(f"\n✅ Workflow complete!")
        print(f"   Escalation needed: {result.get('escalation_needed', False)}")
        print(f"   Recommendations: {len(result.get('ranked_recommendations', []))}")
        print(f"   Confidence: {result.get('confidence', 0):.2%}")
        print(f"   Iterations: {result.get('iteration', 0)}")
        
        # Show workflow messages
        print(f"\n📋 Workflow steps:")
        for msg in result.get("messages", [])[:5]:
            print(f"   - {msg.content}")
        
        return True
    except Exception as e:
        print(f"⚠️  Note: Full workflow requires database. Error: {e}")
        return False


async def test_edge_case_handler():
    """Test edge case handler"""
    print("\n" + "="*60)
    print("TEST 5: Edge Case Handler")
    print("="*60)
    
    from agents.edge_case_handler import EdgeCaseHandler
    
    handler = EdgeCaseHandler()
    
    # Test timezone conflicts
    print("\n🌍 Testing timezone conflict handling...")
    slots = [
        {
            "start_time": datetime.now().replace(hour=22, minute=0),
            "end_time": datetime.now().replace(hour=23, minute=0),
            "confidence": 0.9
        }
    ]
    
    attendee_timezones = {
        "u1": "America/New_York",
        "u2": "Asia/Tokyo",
        "u3": "Europe/London"
    }
    
    fair_slots = handler.handle_timezone_conflicts(slots, attendee_timezones)
    print(f"✅ Original slots: {len(slots)}")
    print(f"✅ Fair slots: {len(fair_slots)}")
    
    # Test all busy scenario
    print("\n⏰ Testing all-busy scenario...")
    alternatives = handler.handle_all_busy(
        ["u1", "u2"],
        datetime.now(),
        datetime.now() + timedelta(days=7),
        60
    )
    print(f"✅ Alternative suggestions: {len(alternatives)}")
    
    return True


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 SCHEDULO AI SYSTEM TEST SUITE")
    print("="*60)
    
    # Check for OpenAI API key
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API key found")
    else:
        print("⚠️  OpenAI API key not set (will use mock responses)")
        print("   Set with: export OPENAI_API_KEY=sk-...")
    
    results = []
    
    # Run tests
    try:
        results.append(("OpenAI Integration", await test_openai_integration()))
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        results.append(("OpenAI Integration", False))
    
    try:
        results.append(("ML Behavior Model", await test_ml_behavior_model()))
    except Exception as e:
        print(f"❌ ML test failed: {e}")
        results.append(("ML Behavior Model", False))
    
    try:
        results.append(("Personal Agent", await test_personal_agent()))
    except Exception as e:
        print(f"❌ Personal Agent test failed: {e}")
        results.append(("Personal Agent", False))
    
    try:
        results.append(("Edge Case Handler", await test_edge_case_handler()))
    except Exception as e:
        print(f"❌ Edge Case test failed: {e}")
        results.append(("Edge Case Handler", False))
    
    try:
        results.append(("LangGraph Orchestrator", await test_langgraph_orchestrator()))
    except Exception as e:
        print(f"❌ LangGraph test failed: {e}")
        results.append(("LangGraph Orchestrator", False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\n{passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! System is ready.")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    print("\n" + "="*60)
    print("Next steps:")
    print("1. Set OPENAI_API_KEY environment variable")
    print("2. Initialize database: python cli.py init && python cli.py seed")
    print("3. Start backend: uvicorn main:app --reload")
    print("4. Test API: curl http://localhost:8000/api/schedule/request")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
