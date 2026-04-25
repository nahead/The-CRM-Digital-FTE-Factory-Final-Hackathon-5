"""
Gemini-based Customer Success Agent
Alternative to OpenAI Agents SDK - uses Google Gemini API (FREE)
"""

import google.generativeai as genai
import os
import json
from typing import List, Dict, Any, Optional
from enum import Enum
import asyncio
from datetime import datetime


class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


class GeminiCustomerAgent:
    """Customer Success Agent powered by Google Gemini"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini agent with API key"""
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        genai.configure(api_key=api_key)

        # Use Gemini 1.5 Flash for fast, free responses
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )

        self.system_prompt = self._load_system_prompt()
        self.tools = self._register_tools()

    def _load_system_prompt(self) -> str:
        """Load system prompt with channel awareness"""
        return """You are a Customer Success agent for TechCorp SaaS (ProjectFlow product).

## Your Purpose
Handle routine customer support queries with speed, accuracy, and empathy across multiple channels.

## Channel Awareness
You receive messages from three channels. Adapt your communication style:
- **Email**: Formal, detailed responses. Include proper greeting and signature.
- **WhatsApp**: Concise, conversational. Keep responses under 300 characters when possible.
- **Web Form**: Semi-formal, helpful. Balance detail with readability.

## Core Behaviors
1. ALWAYS create a ticket at conversation start (include channel!)
2. Check customer history ACROSS ALL CHANNELS before responding
3. Search knowledge base before answering product questions
4. Be concise on WhatsApp, detailed on email
5. Monitor sentiment - escalate if customer becomes frustrated

## Hard Constraints
- NEVER discuss pricing - escalate immediately
- NEVER promise features not in documentation
- NEVER process refunds - escalate to billing
- NEVER share internal processes or systems
- ALWAYS adapt response length to channel

## Escalation Triggers
- Customer mentions "lawyer", "legal", or "sue"
- Customer uses profanity or aggressive language
- Cannot find relevant information after 2 searches
- Customer explicitly requests human help
- WhatsApp customer sends 'human' or 'agent'

## Cross-Channel Continuity
If a customer has contacted us before (any channel), acknowledge it:
"I see you contacted us previously about X. Let me help you further..."

## Available Tools
You have access to these tools (call them using function calling):
- search_knowledge_base: Search product documentation
- create_ticket: Create support ticket with channel tracking
- get_customer_history: Get customer's history across ALL channels
- escalate_to_human: Escalate to human support
- send_response: Send response via appropriate channel

Always use tools to perform actions. Never make up information.
"""

    def _register_tools(self) -> List[Dict]:
        """Register available tools for function calling"""
        return [
            {
                "name": "search_knowledge_base",
                "description": "Search product documentation for relevant information. Use when customer asks about product features, how-to questions, or needs technical information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "create_ticket",
                "description": "Create a support ticket for tracking. ALWAYS create a ticket at the start of every conversation. Include the source channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Customer UUID"
                        },
                        "issue": {
                            "type": "string",
                            "description": "Brief description of the issue"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Priority level"
                        },
                        "category": {
                            "type": "string",
                            "description": "Issue category"
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["email", "whatsapp", "web_form"],
                            "description": "Source channel"
                        }
                    },
                    "required": ["customer_id", "issue", "channel"]
                }
            },
            {
                "name": "get_customer_history",
                "description": "Get customer's complete interaction history across ALL channels. Use to understand context from previous conversations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Customer UUID"
                        }
                    },
                    "required": ["customer_id"]
                }
            },
            {
                "name": "escalate_to_human",
                "description": "Escalate conversation to human support. Use when: customer asks about pricing/refunds, sentiment is negative, cannot find information, or customer requests human help.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket UUID"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for escalation"
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["normal", "high", "urgent"],
                            "description": "Urgency level"
                        }
                    },
                    "required": ["ticket_id", "reason"]
                }
            },
            {
                "name": "send_response",
                "description": "Send response to customer via their channel. Response will be automatically formatted for the channel (email: formal, WhatsApp: concise, web: semi-formal).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket UUID"
                        },
                        "message": {
                            "type": "string",
                            "description": "Response message"
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["email", "whatsapp", "web_form"],
                            "description": "Target channel"
                        }
                    },
                    "required": ["ticket_id", "message", "channel"]
                }
            }
        ]

    async def run(
        self,
        messages: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run the agent with given messages and context

        Args:
            messages: List of conversation messages
            context: Context dict with customer_id, channel, etc.

        Returns:
            Dict with output, tool_calls, escalated status
        """
        try:
            # Build conversation history
            conversation = self._build_conversation(messages, context)

            # Generate response with function calling
            response = await self._generate_with_tools(conversation, context)

            return {
                "output": response.get("text", ""),
                "tool_calls": response.get("tool_calls", []),
                "escalated": response.get("escalated", False),
                "channel": context.get("channel"),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "output": f"Error processing request: {str(e)}",
                "tool_calls": [],
                "escalated": True,
                "error": str(e)
            }

    def _build_conversation(
        self,
        messages: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> str:
        """Build conversation prompt with context"""
        channel = context.get('channel', 'web_form')
        customer_id = context.get('customer_id', 'unknown')

        prompt = f"{self.system_prompt}\n\n"
        prompt += f"## Current Context\n"
        prompt += f"- Channel: {channel}\n"
        prompt += f"- Customer ID: {customer_id}\n"
        prompt += f"- Conversation ID: {context.get('conversation_id', 'new')}\n\n"

        prompt += "## Conversation History\n"
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            prompt += f"{role.upper()}: {content}\n"

        return prompt

    async def _generate_with_tools(
        self,
        conversation: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate response with tool calling support"""

        # For now, simple generation without actual tool execution
        # In production, you'd implement actual tool calling loop
        response = self.model.generate_content(conversation)

        return {
            "text": response.text,
            "tool_calls": [],
            "escalated": self._check_escalation(response.text)
        }

    def _check_escalation(self, text: str) -> bool:
        """Check if response indicates escalation needed"""
        escalation_keywords = [
            "escalate", "human support", "transfer",
            "pricing", "refund", "legal"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in escalation_keywords)


# Singleton instance
_agent_instance = None

def get_agent() -> GeminiCustomerAgent:
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = GeminiCustomerAgent()
    return _agent_instance
