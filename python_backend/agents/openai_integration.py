"""
OpenAI Integration for Natural Language Understanding and Reasoning
"""

from typing import Dict, Any, List, Optional
import os
import json
from openai import AsyncOpenAI
from datetime import datetime


class OpenAIAssistant:
    """
    OpenAI-powered assistant for natural language understanding
    and intelligent reasoning about scheduling
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize OpenAI client
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4")
            self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        else:
            self.client = None
            print(f"⚠️  Warning: OPENAI_API_KEY not set, using mock responses")
        
        # Context about user (built from learned patterns)
        self.user_context = ""
    
    async def query_preferences(
        self,
        query: str,
        learned_patterns: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Answer natural language queries about user preferences
        
        Example queries:
        - "When does Alex prefer to have meetings?"
        - "Will Sarah reschedule internal meetings for client calls?"
        - "What's Marcus's typical meeting pattern?"
        """
        
        # Build context from learned patterns
        context = self._build_context(learned_patterns, user_preferences)
        
        # Use real OpenAI if available
        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are a scheduling assistant analyzing user preferences.
                            
User Context:
{context}

Answer questions about this user's scheduling preferences based on the learned patterns."""
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI API error: {e}")
                return self._mock_preference_response(query, learned_patterns)
        
        # Fallback to mock
        return self._mock_preference_response(query, learned_patterns)
    
    async def resolve_conflict(
        self,
        conflict: Dict[str, Any],
        user_patterns: Dict[str, Any],
        historical_decisions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Use AI reasoning to resolve scheduling conflicts
        
        Returns:
        {
            "resolution": "reschedule_existing" | "find_alternative" | "escalate",
            "reasoning": "explanation",
            "confidence": 0.85,
            "escalate_to_human": False
        }
        """
        
        # Use real OpenAI if available
        if self.client:
            try:
                # Build context
                context = self._build_context(user_patterns, None)
                conflict_desc = json.dumps(conflict, indent=2, default=str)
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are a scheduling assistant resolving conflicts.

User Patterns:
{context}

Analyze the conflict and recommend a resolution. Respond in JSON format:
{{
    "resolution": "reschedule_existing" | "find_alternative" | "escalate",
    "reasoning": "detailed explanation",
    "confidence": 0.0-1.0,
    "escalate_to_human": true/false
}}"""
                        },
                        {
                            "role": "user",
                            "content": f"Resolve this conflict:\n{conflict_desc}"
                        }
                    ]
                )
                
                # Parse JSON from response
                content = response.choices[0].message.content
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(content)
                return result
            except Exception as e:
                print(f"OpenAI API error: {e}")
                return self._mock_conflict_resolution(conflict, user_patterns)
        
        # Fallback to mock
        return self._mock_conflict_resolution(conflict, user_patterns)
    
    async def generate_explanation(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable explanation for recommendation
        
        Example:
        "I recommend Tuesday 2pm because:
        - You typically prefer afternoon meetings (85% acceptance rate)
        - All attendees are available
        - No conflicts with your high-priority meetings
        - Respects your 15-minute buffer preference"
        """
        
        # Use real OpenAI if available
        if self.client:
            try:
                rec_desc = json.dumps(recommendation, indent=2, default=str)
                ctx_desc = json.dumps(context, indent=2, default=str)
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a scheduling assistant explaining recommendations.
                            
Generate a clear, concise explanation for why this time slot is recommended.
Focus on:
- User preferences and patterns
- Attendee availability
- Conflict avoidance
- Meeting context

Keep it friendly and actionable."""
                        },
                        {
                            "role": "user",
                            "content": f"""Explain this recommendation:

Recommendation:
{rec_desc}

Context:
{ctx_desc}"""
                        }
                    ]
                )
                
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI API error: {e}")
                return self._mock_explanation(recommendation, context)
        
        # Fallback to mock
        return self._mock_explanation(recommendation, context)
    
    async def parse_natural_language_request(
        self,
        request: str
    ) -> Dict[str, Any]:
        """
        Parse natural language scheduling request
        
        Example:
        "Schedule a 30-minute sync with Sarah next week, preferably afternoon"
        
        Returns:
        {
            "attendees": ["Sarah"],
            "duration": 30,
            "time_preference": "afternoon",
            "date_range": "next_week",
            "priority": "medium",
            "type": "team_sync"
        }
        """
        
        # Use real OpenAI if available
        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a scheduling assistant parsing natural language requests.

Extract structured information from scheduling requests. Respond in JSON format:
{
    "attendees": ["name1", "name2"],  // List of attendee names
    "duration": 30,  // Duration in minutes (default: 60)
    "time_preference": "morning|afternoon|evening|anytime",  // Time preference
    "date_range": "today|tomorrow|this_week|next_week|specific_date",
    "specific_date": "YYYY-MM-DD",  // If specific date mentioned
    "priority": "low|medium|high",  // Inferred priority
    "type": "team_sync|one_on_one|client_call|interview|other",  // Meeting type
    "notes": "any additional context"
}

If information is not specified, use reasonable defaults."""
                        },
                        {
                            "role": "user",
                            "content": f"Parse this scheduling request: {request}"
                        }
                    ]
                )
                
                # Parse JSON from response
                content = response.choices[0].message.content
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(content)
                return result
            except Exception as e:
                print(f"OpenAI API error: {e}")
                return self._mock_parse_request(request)
        
        # Fallback to mock
        return self._mock_parse_request(request)
    
    async def update_context(self, feedback: Dict[str, Any]):
        """Update user context based on feedback"""
        # TODO: Update context for future queries
        pass
    
    def _build_context(
        self,
        learned_patterns: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]]
    ) -> str:
        """Build context string for OpenAI"""
        context_parts = []
        
        # Time preferences
        if "time_preferences" in learned_patterns:
            best_hours = [
                h for h, rate in learned_patterns["time_preferences"].items()
                if rate > 0.7
            ]
            if best_hours:
                context_parts.append(f"Prefers meetings at hours: {best_hours}")
        
        # Day preferences
        if "day_preferences" in learned_patterns:
            best_days = [
                ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d]
                for d, rate in learned_patterns["day_preferences"].items()
                if rate > 0.7
            ]
            if best_days:
                context_parts.append(f"Prefers days: {', '.join(best_days)}")
        
        # Reschedule patterns
        if "reschedule_patterns" in learned_patterns:
            high_reschedule = [
                mtype for mtype, rate in learned_patterns["reschedule_patterns"].items()
                if rate > 0.5
            ]
            if high_reschedule:
                context_parts.append(f"Often reschedules: {', '.join(high_reschedule)}")
        
        return "\n".join(context_parts)
    
    def _mock_preference_response(
        self,
        query: str,
        learned_patterns: Dict[str, Any]
    ) -> str:
        """Mock response for preference queries"""
        # TODO: Replace with real OpenAI call
        return f"Based on {learned_patterns.get('training_samples', 0)} historical meetings, the user prefers afternoon meetings and avoids Friday afternoons."
    
    def _mock_conflict_resolution(
        self,
        conflict: Dict[str, Any],
        user_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock conflict resolution"""
        # TODO: Replace with real OpenAI reasoning
        return {
            "resolution": "reschedule_existing",
            "reasoning": "User typically reschedules internal meetings for client calls",
            "confidence": 0.85,
            "escalate_to_human": False
        }
    
    def _mock_explanation(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Mock explanation generation"""
        # TODO: Replace with real OpenAI generation
        return "This time works well based on your typical scheduling patterns."
    
    def _mock_parse_request(self, request: str) -> Dict[str, Any]:
        """Mock NLP parsing"""
        # TODO: Replace with real OpenAI parsing
        return {
            "attendees": [],
            "duration": 30,
            "priority": "medium",
            "type": "team_sync"
        }
