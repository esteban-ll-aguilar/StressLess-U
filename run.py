from sys import exit
from dotenv import load_dotenv
import os

from apps.config import config_dict
from apps import create_app

# Load environment variables from .env file
load_dotenv()

# WARNING: Don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)

if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG))
    app.logger.info('Environment = ' + get_config_mode)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(
        host='0.0.0.0', 
        port=port,
        )
else:
    # This is for Gunicorn to use
    gunicorn_app = app