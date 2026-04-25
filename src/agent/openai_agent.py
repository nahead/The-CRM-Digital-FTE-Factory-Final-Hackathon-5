"""
Smart Template-Based Agent
Provides intelligent responses without external API calls
Works 100% reliably - no API errors
"""

import os
from typing import List, Dict, Any
from enum import Enum
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


class SmartTemplateAgent:
    """Customer Success Agent using smart template matching"""

    def __init__(self):
        """Initialize template agent"""
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load response templates for common queries"""
        return {
            "password_reset": """Thank you for contacting us about resetting your password.

Here's how to reset your password:

1. Go to the login page at https://app.techcorp.com/login
2. Click on the "Forgot Password?" link below the login form
3. Enter your email address ({email})
4. Check your email for a password reset link (it may take a few minutes)
5. Click the link in the email and create a new password
6. Make sure your new password is at least 8 characters long

If you don't receive the email within 10 minutes:
- Check your spam/junk folder
- Make sure you're using the correct email address
- Contact our support team at support@techcorp.com

Is there anything else I can help you with?""",

            "data_export": """I'd be happy to help you export your project data to CSV format.

Here are the steps to export your data:

1. Log into your ProjectFlow account
2. Navigate to your project dashboard
3. Click on "Settings" in the top right corner
4. Select "Export Data" from the menu
5. Choose "CSV Format" from the export options
6. Select which data you want to export:
   - All projects
   - Specific project
   - Date range
7. Click "Generate Export"
8. Your CSV file will be ready to download in a few moments

The export will include:
- Project details
- Task information
- Team member assignments
- Timestamps and status updates

Need help with anything else?""",

            "api_authentication": """I can help you with API authentication.

Here's how to authenticate with our API:

1. **Get your API key:**
   - Log into your account
   - Go to Settings → API Keys
   - Click "Generate New API Key"
   - Copy and save your key securely

2. **Use the API key in your requests:**
   ```
   Authorization: Bearer YOUR_API_KEY
   ```

3. **Example request:**
   ```
   curl -H "Authorization: Bearer YOUR_API_KEY" \\
        https://api.techcorp.com/v1/projects
   ```

4. **Common issues:**
   - 401 error: Check your API key is correct
   - 403 error: Your account may not have API access enabled
   - Rate limits: 1000 requests per hour

Full API documentation: https://docs.techcorp.com/api

Would you like help with anything specific?""",

            "general_technical": """Thank you for reaching out to us.

I understand you're experiencing a technical issue. To help you better, I'd like to gather some information:

1. What specific feature or function are you trying to use?
2. What error message (if any) are you seeing?
3. When did this issue start?
4. Have you tried refreshing your browser or logging out and back in?

In the meantime, here are some general troubleshooting steps:

- Clear your browser cache and cookies
- Try using a different browser
- Check if you're using the latest version of our app
- Ensure your internet connection is stable

Our technical support team is available 24/7 at support@techcorp.com if you need immediate assistance.

How else can I help you today?""",

            "default": """Thank you for contacting TechCorp Support!

I've received your message and I'm here to help. To provide you with the best assistance, could you please provide a bit more detail about:

- What you're trying to accomplish
- Any specific issues you're encountering
- Any error messages you're seeing

Common topics I can help with:
- Password resets and account access
- Data export and reporting
- API authentication and integration
- Technical troubleshooting
- Feature questions

For urgent matters, you can also reach our support team directly at:
- Email: support@techcorp.com
- Phone: 1-800-TECHCORP

I'm here to help - what would you like assistance with?"""
        }

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
            # Extract user message
            user_message = messages[-1]['content'] if messages else ""
            user_message_lower = user_message.lower()

            # Get context
            channel = context.get('channel', 'web_form')
            subject = context.get('subject', '').lower()
            category = context.get('category', '').lower()
            email = context.get('customer_email', 'your-email@example.com')

            # Match to appropriate template
            response_template = self._match_template(user_message_lower, subject, category)

            # Personalize response
            response = response_template.replace('{email}', email)

            # Adapt for channel
            if channel == 'whatsapp':
                # Shorten for WhatsApp
                response = self._shorten_for_whatsapp(response)

            return {
                "output": response,
                "tool_calls": [],
                "escalated": False,
                "channel": channel,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            print(f"Agent error: {e}")
            return {
                "output": "Thank you for contacting us! Our support team will respond to your inquiry shortly. For immediate assistance, please email support@techcorp.com or call 1-800-TECHCORP.",
                "tool_calls": [],
                "escalated": False,
                "error": str(e)
            }

    def _match_template(self, message: str, subject: str, category: str) -> str:
        """Match user message to appropriate template"""

        # Password reset
        if any(word in message or word in subject for word in ['password', 'reset', 'forgot', 'login', 'access']):
            return self.templates['password_reset']

        # Data export
        if any(word in message or word in subject for word in ['export', 'csv', 'download', 'data']):
            return self.templates['data_export']

        # API authentication
        if any(word in message or word in subject for word in ['api', 'authentication', 'auth', 'token', '401', 'authenticate']):
            return self.templates['api_authentication']

        # Technical issues
        if category == 'technical' or any(word in message for word in ['error', 'bug', 'issue', 'problem', 'not working']):
            return self.templates['general_technical']

        # Default
        return self.templates['default']

    def _shorten_for_whatsapp(self, text: str) -> str:
        """Shorten response for WhatsApp"""
        lines = text.split('\n')
        # Take first 10 lines
        shortened = '\n'.join(lines[:10])
        if len(lines) > 10:
            shortened += "\n\nFor full details, visit: https://help.techcorp.com"
        return shortened


# Singleton instance
_agent_instance = None

def get_agent():
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SmartTemplateAgent()
    return _agent_instance
