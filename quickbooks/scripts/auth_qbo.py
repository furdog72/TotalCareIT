"""
QuickBooks Online OAuth authentication script
Run this first to get your access tokens
"""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

# Load environment variables
load_dotenv()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        print("\n" + "="*60)

        if 'code' in params and 'realmId' in params:
            auth_code = params['code'][0]
            realm_id = params['realmId'][0]

            print("Authorization successful!")
            print(f"Realm ID (Company ID): {realm_id}")

            # Exchange code for tokens
            try:
                client_id = os.getenv('QBO_CLIENT_ID')
                client_secret = os.getenv('QBO_CLIENT_SECRET')
                redirect_uri = os.getenv('QBO_REDIRECT_URI')
                environment = os.getenv('QBO_ENVIRONMENT', 'sandbox')

                auth_client = AuthClient(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    environment=environment,
                )

                auth_client.get_bearer_token(auth_code, realm_id=realm_id)

                # Save tokens to file
                with open('.qbo_tokens', 'w') as f:
                    f.write(f"ACCESS_TOKEN={auth_client.access_token}\n")
                    f.write(f"REFRESH_TOKEN={auth_client.refresh_token}\n")
                    f.write(f"REALM_ID={realm_id}\n")

                print("Tokens saved to .qbo_tokens")
                print(f"\nMake sure your .env file has:")
                print(f"QBO_COMPANY_ID={realm_id}")

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                    <body>
                        <h1>Authorization Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                    </body>
                    </html>
                """)

            except Exception as e:
                print(f"Error: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"<html><body><h1>Error</h1><p>{e}</p></body></html>".encode())

        else:
            error = params.get('error', ['Unknown error'])[0]
            print(f"Authorization failed: {error}")

            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Error</h1><p>{error}</p></body></html>".encode())

        print("="*60 + "\n")

    def log_message(self, format, *args):
        pass  # Suppress default logging


def main():
    # Get config from environment
    client_id = os.getenv('QBO_CLIENT_ID')
    client_secret = os.getenv('QBO_CLIENT_SECRET')
    redirect_uri = os.getenv('QBO_REDIRECT_URI')
    environment = os.getenv('QBO_ENVIRONMENT', 'sandbox')

    if not client_id or not client_secret:
        print("Error: QBO_CLIENT_ID and QBO_CLIENT_SECRET must be set in .env file")
        return

    # Create auth client
    auth_client = AuthClient(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        environment=environment,
    )

    # Get authorization URL
    auth_url = auth_client.get_authorization_url([Scopes.ACCOUNTING])

    print("\n" + "="*60)
    print("QuickBooks OAuth Authentication")
    print("="*60)
    print(f"\nEnvironment: {environment}")
    print("\n1. Starting local server on http://localhost:8000")
    print("\n2. Visit this URL to authorize:")
    print(f"\n   {auth_url}")
    print("\n3. After authorization, come back here")
    print("="*60 + "\n")

    # Start server
    server = HTTPServer(('localhost', 8000), OAuthCallbackHandler)
    print("Waiting for OAuth callback...\n")

    try:
        server.handle_request()
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
