"""
Simple OAuth callback server to capture authorization code and realm_id
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from qbo_ai import QBOClient


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the callback URL
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        print("\n" + "="*60)
        print("Callback received!")
        print("="*60)

        # Check for authorization code and realm_id
        if 'code' in params and 'realmId' in params:
            auth_code = params['code'][0]
            realm_id = params['realmId'][0]

            print(f"Authorization Code: {auth_code}")
            print(f"Realm ID (Company ID): {realm_id}")
            print("="*60)

            # Exchange code for tokens
            try:
                print("\nExchanging code for tokens...")
                client = QBOClient()
                tokens = client.get_bearer_token(auth_code, realm_id)

                print(f"Access Token: {tokens['access_token'][:20]}...")
                print(f"Refresh Token: {tokens['refresh_token'][:20]}...")

                # Save tokens to file
                import os
                tokens_file = os.path.join(os.path.dirname(__file__), '..', '.qbo_tokens')
                with open(tokens_file, 'w') as f:
                    f.write(f"ACCESS_TOKEN={tokens['access_token']}\n")
                    f.write(f"REFRESH_TOKEN={tokens['refresh_token']}\n")
                    f.write(f"REALM_ID={tokens['realm_id']}\n")

                print(f"\nTokens saved to: {tokens_file}")

            except Exception as e:
                print(f"\nError getting tokens: {e}")

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <p>Tokens have been saved and you can now query QuickBooks data.</p>
                </body>
                </html>
            """)

            print("\nAdd this to your .env file:")
            print(f"QBO_COMPANY_ID={realm_id}")
            print("="*60 + "\n")

        elif 'error' in params:
            error = params.get('error', ['unknown'])[0]
            error_description = params.get('error_description', ['No description'])[0]

            print(f"ERROR: {error}")
            print(f"Description: {error_description}")
            print("="*60)

            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <body>
                    <h1>Authorization Failed</h1>
                    <p><strong>Error:</strong> {error}</p>
                    <p><strong>Description:</strong> {error_description}</p>
                    <p>Check your terminal for more details.</p>
                </body>
                </html>
            """.encode())
        else:
            print("Unexpected callback format")
            print(f"Path: {self.path}")
            print(f"Params: {params}")

            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Unexpected Callback</h1>
                    <p>Check your terminal for details.</p>
                </body>
                </html>
            """)

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def main():
    # Initialize client and get auth URL
    client = QBOClient()
    auth_url = client.get_authorization_url()

    print("\n" + "="*60)
    print("QuickBooks OAuth Flow")
    print("="*60)
    print("\n1. Starting local server on http://localhost:8000")
    print("\n2. Visit this URL to authorize:")
    print(f"\n   {auth_url}")
    print("\n3. After authorization, the browser will redirect back here")
    print("\n" + "="*60 + "\n")

    # Start server
    server = HTTPServer(('localhost', 8000), OAuthCallbackHandler)
    print("Waiting for OAuth callback...\n")

    try:
        # Handle one request then exit
        server.handle_request()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
