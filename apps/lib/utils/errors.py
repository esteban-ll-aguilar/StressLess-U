from functools import wraps
from flask import abort, render_template, current_app
from flask_login import current_user
import logging
import traceback
from jinja2.exceptions import TemplateNotFound
from datetime import datetime

logger = logging.getLogger(__name__)

def format_error_details(error):
    """Formatea los detalles del error para el registro y visualización"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_type = type(error).__name__
    error_message = str(error)
    stack_trace = traceback.format_exc()
    
    return f"""Timestamp: {timestamp}
Error Type: {error_type}
Message: {error_message}
Stack Trace:
{stack_trace}"""


def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except TemplateNotFound as e:
            error_details = format_error_details(e)
            logger.error(f"❌​ ​Template not found:\n{error_details}")
            return render_template(
                'errors/404.html',
                description="{{ _('Sorry, we could not find the requested template. Please try again later.') }}",
                error_details=error_details 
            ), 404
        except Exception as e:
            error_details = format_error_details(e)
            logger.error(f"❌​ ​Unexpected error:\n{error_details}")
            return render_template(
                'errors/500.html',
                description="{{ _('Sorry, an unexpected error has occurred. Our team has been notified and we are working to fix it.') }}",
                error_details=error_details 
            ), 500

    return decorated_function

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        error_details = format_error_details(error)
        logger.error(f"❌​ ​Page not found:\n{error_details}")
        return render_template(
            'errors/404.html',
            description="{{ _('Sorry, the page you are looking for does not exist.') }}",
            error_details=error_details 
        ), 404

    @app.errorhandler(500)
    def internal_error(error):
        error_details = format_error_details(error)
        logger.error(f"❌​ ​Internal Server Error:\n{error_details}")
        return render_template(
            'errors/500.html',
            description=str(error.description) if hasattr(error, 'description') else "{{ _('An internal server error has occurred.') }}",
            error_details=error_details 
        ), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        error_details = format_error_details(error)
        logger.error(f"❌​ ​Forbidden access:\n{error_details}")
        return render_template(
            'errors/403.html',
            description="{{ _('Sorry, you do not have permission to access this resource.') }}",
            error_details=error_details 
        ), 403

    @app.errorhandler(401)
    def unauthorized_error(error):
        error_details = format_error_details(error)
        logger.error(f"❌​ ​Unauthorized access:\n{error_details}")
        return render_template(
            'errors/401.html',
            description="{{ _('Please log in to access this resource.') }}",
            error_details=error_details 
        ), 401

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        error_details = format_error_details(error)
        logger.error(f"❌​ ​Unexpected Error:\n{error_details}")
        return render_template(
            'errors/500.html',
            description="{{ _('An unexpected error has occurred. Please try again later.') }}",
            error_details=error_details 
        ), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        error_details = format_error_details(error)
        logger.error(f"❌​ ​Bad Request:\n{error_details}")
        return render_template(
            'errors/500.html',
            description="{{ _('The request could not be processed. Please verify the data sent.') }}",
            error_details=error_details 
        ), 400

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        error_details = format_error_details(error)
        logger.error(f"❌​ ​Method Not Allowed:\n{error_details}")
        return render_template(
            'errors/500.html',
            description="{{ _('The request method is not allowed for this URL.') }}",
            error_details=error_details 
        ), 405

    @app.errorhandler(408)
    def request_timeout_error(error):
        error_details = format_error_details(error)
        logger.error(f"❌​ ​Request Timeout:\n{error_details}")
        return render_template(
            'errors/500.html',
            description="{{ _('The request has timed out. Please try again.') }}",
            error_details=error_details 
        ), 408

    @app.errorhandler(429)
    def too_many_requests_error(error):
        error_details = format_error_details(error)
        logger.error(f"❌​ ​Too Many Requests:\n{error_details}")
        return render_template(
            'errors/500.html',
            description="{{ _('You have made too many requests. Please wait a moment before trying again.') }}",
            error_details=error_details 
        ), 429
