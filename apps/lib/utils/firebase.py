import json
import os
from apps.lib.utils.files import download_file, check_file_exists


REQUIRED_FIREBASE_FIELDS = [
    "apiKey", "authDomain", "projectId", 
    "storageBucket", "messagingSenderId", "appId"
]

def load_config(config_file_path):
    """Load and validate Firebase configuration from a JSON file."""
    with open(config_file_path, "r") as file:
        config = json.load(file)

    for field in REQUIRED_FIREBASE_FIELDS:
        if field not in config:
            raise KeyError(f"❌​ ​Missing required field '{field}' in Firebase configuration")

    config.setdefault("measurementId", None)  # Optional field
    return config

def check_firebase_files(config_file, service_acc_file, client_secrets_file):
    """Check and validate Firebase configuration and service account files."""
    print("Checking Firebase files")
    check_file_exists(config_file, "Firebase configuration file")
    check_file_exists(service_acc_file, "Firebase service account file")
    check_file_exists(client_secrets_file, "Firebase client secrets file")
    load_config(config_file)  # Validate configuration file structure

def download_missing_files(service_acc_url, app_config_url,clien_secret_url, destination_path):
    """Download Firebase credential files if they are missing."""
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    download_file(service_acc_url, os.path.join(destination_path, 'serviceAccountKey.json'))
    download_file(app_config_url, os.path.join(destination_path, 'firebase-app-config.json'))
    download_file(clien_secret_url, os.path.join(destination_path, 'client_secrets.json'))


def get_firebase_cred_files():
    """Retrieve and validate Firebase configuration and service account files."""
    print("Getting Firebase credential files")
    basedir = os.getcwd()
    firebase_path = os.path.join(basedir, 'credentials', 'firebase')
    
    service_account_path = os.path.join(firebase_path, 'serviceAccountKey.json')
    config_app_path = os.path.join(firebase_path, "firebase-app-config.json")
    client_secrets_path = os.path.join(firebase_path, "client_secrets.json")

    if not os.path.exists(service_account_path) or not \
            os.path.exists(config_app_path) or not \
            os.path.exists(client_secrets_path):
        service_acc_url = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_FILE')
        app_config_url = os.getenv('FIREBASE_APP_CONFIG_FILE')
        clien_secret_url = os.getenv('FIREBASE_CLIENT_SECRETS_FILE')

        if not service_acc_url or not app_config_url:
            raise EnvironmentError("Firebase credential URLs are not set in environment variables")

        download_missing_files(service_acc_url, app_config_url, clien_secret_url,firebase_path)

    check_firebase_files(config_app_path, service_account_path, client_secrets_path)
    
    return service_account_path, config_app_path
