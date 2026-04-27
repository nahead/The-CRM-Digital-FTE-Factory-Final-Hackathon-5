"""
Email Handler via Gmail API
Handles incoming emails and sends responses
"""

import os
import base64
import pickle
from email.mime.text import MIMEText
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class EmailHandler:
    """Handle Gmail integration via Gmail API"""

    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize Gmail handler.

        Args:
            credentials_path: Path to credentials.json from Google Cloud
            token_path: Path to store/load token.pickle
        """
        self.credentials_path = credentials_path or os.getenv(
            'GMAIL_CREDENTIALS_PATH',
            'credentials/gmail_credentials.json'
        )
        self.token_path = token_path or os.getenv(
            'GMAIL_TOKEN_PATH',
            'credentials/gmail_token.pickle'
        )

        self.creds = None
        self.service = None

        # Try to authenticate, but don't fail if credentials are missing
        try:
            self._authenticate()
        except Exception as e:
            print(f"Gmail authentication skipped: {e}")
            print("Email notifications will not be sent, but responses will be stored in database")

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2"""
        # Try to load credentials from environment variable first (for Render.com)
        gmail_creds_json = os.getenv('GMAIL_CREDENTIALS_JSON')
        if gmail_creds_json:
            import json
            import tempfile
            # Write credentials to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(gmail_creds_json)
                temp_creds_path = f.name
            self.credentials_path = temp_creds_path

        # Try to load token from environment variable
        gmail_token_base64 = os.getenv('GMAIL_TOKEN_BASE64')
        if gmail_token_base64:
            import base64
            token_data = base64.b64decode(gmail_token_base64)
            self.creds = pickle.loads(token_data)
        # Load token from file if exists
        elif os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # If no valid credentials, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Gmail credentials not found at {self.credentials_path}. "
                        "Download from Google Cloud Console."
                    )

                # Note: This requires interactive authentication and won't work on Render
                # You need to generate token locally and set GMAIL_TOKEN_BASE64 env var
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save token for future use (only works locally)
            if not gmail_token_base64:
                os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.creds, token)

        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=self.creds)
        print("Gmail handler authenticated successfully")

    def check_inbox(self, max_results: int = 10) -> List[Dict]:
        """
        Check inbox for new unread messages.

        Args:
            max_results: Maximum number of messages to retrieve

        Returns:
            List of normalized message dictionaries
        """
        try:
            messages = self.get_unread_messages(max_results)

            # Mark messages as read after fetching
            for msg in messages:
                if msg.get('channel_message_id'):
                    self.mark_as_read(msg['channel_message_id'])

            return messages

        except Exception as error:
            print(f"Error checking inbox: {error}")
            return []

    def get_unread_messages(self, max_results: int = 10) -> List[Dict]:
        """
        Get unread messages from inbox.

        Args:
            max_results: Maximum number of messages to retrieve

        Returns:
            List of message dictionaries
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            parsed_messages = []
            for msg in messages:
                message_data = self._get_message_details(msg['id'])
                if message_data:
                    parsed_messages.append(message_data)

            return parsed_messages

        except HttpError as error:
            print(f"Error fetching messages: {error}")
            return []

    def _get_message_details(self, message_id: str) -> Optional[Dict]:
        """
        Get full message details.

        Args:
            message_id: Gmail message ID

        Returns:
            Normalized message dictionary
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']

            # Extract headers
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
            to_email = next((h['value'] for h in headers if h['name'] == 'To'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

            # Extract body
            body = self._get_message_body(message['payload'])

            # Parse email address
            email_address = self._parse_email_address(from_email)
            sender_name = self._parse_sender_name(from_email)

            return {
                'channel': 'email',
                'channel_message_id': message_id,
                'customer_email': email_address,
                'customer_name': sender_name,
                'subject': subject,
                'content': body,
                'received_at': date,
                'thread_id': message.get('threadId'),
                'metadata': {
                    'to': to_email,
                    'labels': message.get('labelIds', []),
                    'snippet': message.get('snippet', '')
                }
            }

        except HttpError as error:
            print(f"Error getting message details: {error}")
            return None

    def _get_message_body(self, payload: Dict) -> str:
        """Extract message body from payload"""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')

        # If no parts, try direct body
        if 'body' in payload and 'data' in payload['body']:
            data = payload['body']['data']
            return base64.urlsafe_b64decode(data).decode('utf-8')

        return ""

    def _parse_email_address(self, from_header: str) -> str:
        """Extract email address from 'From' header"""
        # Format: "Name <email@example.com>" or "email@example.com"
        if '<' in from_header and '>' in from_header:
            start = from_header.index('<') + 1
            end = from_header.index('>')
            return from_header[start:end]
        return from_header.strip()

    def _parse_sender_name(self, from_header: str) -> str:
        """Extract sender name from 'From' header"""
        if '<' in from_header:
            return from_header.split('<')[0].strip().strip('"')
        return self._parse_email_address(from_header)

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None
    ) -> Dict:
        """
        Send email via Gmail API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            thread_id: Optional thread ID for replies

        Returns:
            Send result with message ID
        """
        try:
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject

            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')

            send_params = {
                'userId': 'me',
                'body': {'raw': raw_message}
            }

            # Add thread ID for replies
            if thread_id:
                send_params['body']['threadId'] = thread_id

            result = self.service.users().messages().send(**send_params).execute()

            return {
                'channel_message_id': result['id'],
                'thread_id': result.get('threadId'),
                'delivery_status': 'sent'
            }

        except HttpError as error:
            print(f"Error sending email: {error}")
            return {'delivery_status': 'failed', 'error': str(error)}

    def mark_as_read(self, message_id: str):
        """Mark message as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except HttpError as error:
            print(f"Error marking as read: {error}")

    def format_response(
        self,
        response: str,
        customer_name: str,
        ticket_id: str
    ) -> str:
        """
        Format response for email channel.

        Args:
            response: AI-generated response
            customer_name: Customer's name
            ticket_id: Ticket ID

        Returns:
            Formatted email body
        """
        return f"""Hi {customer_name},

{response}

If you have any further questions, please don't hesitate to reach out.

Best regards,
TechCorp Support Team

---
Ticket ID: {ticket_id}
This is an automated response from our AI assistant.
"""

    def setup_push_notifications(self, webhook_url: str, topic_name: str):
        """
        Setup Gmail push notifications via Pub/Sub.

        Args:
            webhook_url: Your webhook URL
            topic_name: Google Cloud Pub/Sub topic name

        Note: Requires Google Cloud Pub/Sub setup
        """
        try:
            request = {
                'labelIds': ['INBOX'],
                'topicName': topic_name
            }

            result = self.service.users().watch(
                userId='me',
                body=request
            ).execute()

            print(f"Push notifications enabled. Expires: {result['expiration']}")
            return result

        except HttpError as error:
            print(f"Error setting up push notifications: {error}")
            return None
