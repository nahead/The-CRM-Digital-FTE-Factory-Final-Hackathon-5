"""
Generate base64 encoded Gmail token for Render.com deployment
"""
import base64
import os

def generate_token_base64():
    """Generate base64 encoded token from gmail_token.pickle"""
    token_path = 'credentials/gmail_token.pickle'

    if not os.path.exists(token_path):
        print(f"[ERROR] Token file not found: {token_path}")
        print("\nYou need to run the Gmail authentication locally first:")
        print("1. Make sure gmail_credentials.json is in credentials/")
        print("2. Run: python src/api/main.py")
        print("3. Complete OAuth flow in browser")
        print("4. Token will be saved to credentials/gmail_token.pickle")
        return None

    print(f"Reading token from: {token_path}")
    with open(token_path, 'rb') as f:
        token_data = f.read()

    # Encode to base64
    token_base64 = base64.b64encode(token_data).decode('utf-8')

    print("\n" + "="*80)
    print("GMAIL TOKEN (Base64 Encoded)")
    print("="*80)
    print("\nCopy this value and add to Render environment variables:")
    print("\nKey: GMAIL_TOKEN_BASE64")
    print(f"Value: {token_base64}")
    print("\n" + "="*80)

    return token_base64

def generate_credentials_json():
    """Read and format credentials JSON"""
    creds_path = 'credentials/gmail_credentials.json'

    if not os.path.exists(creds_path):
        print(f"\n[ERROR] Credentials file not found: {creds_path}")
        return None

    print(f"\nReading credentials from: {creds_path}")
    with open(creds_path, 'r') as f:
        creds_json = f.read()

    print("\n" + "="*80)
    print("GMAIL CREDENTIALS JSON")
    print("="*80)
    print("\nCopy this value and add to Render environment variables:")
    print("\nKey: GMAIL_CREDENTIALS_JSON")
    print(f"Value: {creds_json}")
    print("\n" + "="*80)

    return creds_json

if __name__ == "__main__":
    print("Gmail Credentials Generator for Render.com")
    print("="*80)

    # Generate credentials JSON
    creds = generate_credentials_json()

    # Generate token base64
    token = generate_token_base64()

    if creds and token:
        print("\n[OK] Both credentials generated successfully!")
        print("\nNext steps:")
        print("1. Go to Render Dashboard -> fte-backend -> Environment")
        print("2. Add GMAIL_CREDENTIALS_JSON with the JSON value above")
        print("3. Add GMAIL_TOKEN_BASE64 with the base64 value above")
        print("4. Save and redeploy")
    else:
        print("\n[ERROR] Failed to generate credentials")
