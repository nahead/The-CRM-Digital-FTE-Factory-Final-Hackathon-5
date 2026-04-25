"""
Gmail Handler for Email Channel
Handles incoming emails via Gmail API and sends responses
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import base64
import email
from email.mime.text import MIMEText
from datetime import datetime
import json
import os
from typing import Dict, List, Optional


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class GmailHandler:
    """Handle Gmail integration for email support"""

    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize Gmail handler with credentials"""
        self.credentials_path = credentials_path or os.getenv(
            'GMAIL_CREDENTIALS_PATH',
            './credentials/gmail_credentials.json'
        )
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        token_path = './credentials/gmail_token.json'

        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # Refresh or get new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Gmail credentials not found at {self.credentials_path}. "
                        "Please download from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

    async def setup_push_notifications(self, topic_name: str) -> Dict:
        """
        Set up Gmail push notifications via Pub/Sub.

        Args:
            topic_name: Google Cloud Pub/Sub topic name

        Returns:
            Watch response
        """
        request = {
            'labelIds': ['INBOX'],
            'topicName': topic_name,
            'labelFilterAction': 'include'
        }
        return self.service.users().watch(userId='me', body=request).execute()

    async def get_message(self, message_id: str) -> Dict:
        """
        Fetch and parse a Gmail message.

        Args:
            message_id: Gmail message ID

        Returns:
            Normalized message dict
        """
        msg = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

        headers = {h['name']: h['value'] for h in msg['payload']['headers']}

        # Extract body
        body = self._extract_body(msg['payload'])

        return {
            'channel': 'email',
            'channel_message_id': message_id,
            'customer_email': self._extract_email(headers.get('From', '')),
            'customer_name': self._extract_name(headers.get('From', '')),
            'subject': headers.get('Subject', ''),
            'content': body,
            'received_at': datetime.utcnow().isoformat(),
            'thread_id': msg.get('threadId'),
            'metadata': {
                'headers': headers,
                'labels': msg.get('labelIds', [])
            }
        }

    def _extract_body(self, payload: Dict) -> str:
        """Extract text body from email payload"""
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    # Fallback to HTML if no plain text
                    html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    # Simple HTML stripping (in production, use proper HTML parser)
                    import re
                    return re.sub('<[^<]+?>', '', html)

        return ''

    def _extract_email(self, from_header: str) -> str:
        """Extract email address from From header"""
        import re
        match = re.search(r'<(.+?)>', from_header)
        return match.group(1) if match else from_header.strip()

    def _extract_name(self, from_header: str) -> str:
        """Extract name from From header"""
        import re
        match = re.search(r'^(.+?)\s*<', from_header)
        return match.group(1).strip('"') if match else ''

    async def send_reply(
        self,
        to_email: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None
    ) -> Dict:
        """
        Send email reply.

        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            thread_id: Thread ID for reply

        Returns:
            Send result with message ID
        """
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        send_request = {'raw': raw}
        if thread_id:
            send_request['threadId'] = thread_id

        result = self.service.users().messages().send(
            userId='me',
            body=send_request
        ).execute()

        return {
            'channel_message_id': result['id'],
            'delivery_status': 'sent'
        }

    async def list_unread_messages(self, max_results: int = 10) -> List[Dict]:
        """
        List unread messages from inbox.

        Args:
            max_results: Maximum number of messages

        Returns:
            List of message dicts
        """
        results = self.service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            maxResults=max_results
        ).execute()

        messages = []
        for msg in results.get('messages', []):
            message = await self.get_message(msg['id'])
            messages.append(message)

        return messages
