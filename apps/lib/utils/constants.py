
import os

SCOPES = os.getenv('GOOGLE_OAUTH_SCOPES','').split(',')

CLIENT_SECRETS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname((__file__))))),
    "credentials/firebase/client_secrets.json"
)