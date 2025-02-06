# Flask Gradient Able Pro Template

A professional Flask Dashboard template integrated with Firebase Authentication, featuring a modern UI design based on the Gradient Able Pro theme. This template provides a solid foundation for building web applications with user authentication, multilingual support, and a comprehensive admin interface.

## Features

### Core Features
- Firebase Authentication integration
- Multi-language support (i18n)
- Debug and Production modes
- Modular architecture
- Responsive design
- Dark/Light mode support

### UI Components
- Modern dashboard layout
- Comprehensive UI components library
- Interactive charts and graphs
- Data tables with advanced features
- Form elements and validation
- Notification system
- File upload functionality

### Security Features
- Secure authentication flow
- Session management
- CSRF protection
- Environment-based configurations
- Secure password handling

### Development Features
- Hot reload in development
- Modular blueprint structure
- Easy customization
- Comprehensive documentation
- Translation management system

## Requirements

- Python 3.8+
- Firebase Project
- Virtual Environment
- Node.js (for asset compilation)

## Quick Start

### 1. Clone the repository
```bash
git clone <repository-url>
cd Flask_Gradient_Able_ProTemplate
```

### 2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Firebase Configuration

1. Create a project in Firebase Console
2. Download serviceAccountKey.json from Project Settings > Service Accounts
3. Get Firebase configuration (firebase-app-config.json)
4. Create directory: `credentials/firebase/`
5. Place both files in `credentials/firebase/`

### 4. Environment Configuration

Copy .env.sample to .env:
```bash
cp .env.sample .env
```

Required variables:
```
SECRET_KEY=your-secret-key
FIREBASE_SERVICE_ACCOUNT_KEY_FILE=credentials/firebase/serviceAccountKey.json
FIREBASE_APP_CONFIG_FILE=credentials/firebase/firebase-app-config.json
BABEL_DEFAULT_LOCALE=en
```

## Project Structure

```
Flask_Gradient_Able_ProTemplate/
├── apps/
│   ├── authentication/    # Authentication module
│   │   ├── forms.py      # Form definitions
│   │   ├── models.py     # User models
│   │   ├── routes.py     # Auth routes
│   │   └── services.py   # Auth services
│   ├── dashboard/        # Dashboard module
│   ├── home/            # Main application module
│   ├── static/          # Static files
│   │   ├── assets/      # Theme assets
│   │   ├── css/         # Custom CSS
│   │   └── js/          # Custom JavaScript
│   ├── templates/       # HTML templates
│   │   ├── accounts/    # Auth templates
│   │   ├── includes/    # Reusable components
│   │   └── layouts/     # Base layouts
│   └── lib/            # Utilities and helpers
├── credentials/        # Configuration files
├── translations/       # Language files
└── requirements.txt   # Project dependencies
```

## Running the Application

### Development Mode
```bash
# Start the development server
flask run

# Access the application
# Navigate to http://localhost:5000
```

### Production Mode
```bash
# Using Gunicorn
gunicorn --config gunicorn-cfg.py run:app
```

## Translation Management

The application supports multiple languages through Flask-Babel. Translation files are stored in the `translations/` directory.

### Translation Commands
```bash
# Extract texts for translation
pybabel extract -F babel.cfg -o messages.pot .

# Create a new language
pybabel init -i messages.pot -d translations -l [language_code]

# Update translations
pybabel update -i messages.pot -d translations

# Compile translations
pybabel compile -d translations
```

You can easily translate .pot files using online tools like [PO Translator](https://www.ajexperience.com/po-translator/)

## Customization Guide

### Theme Customization
1. Modify `apps/static/assets/scss/` for styling changes
2. Update `apps/templates/layouts/` for layout modifications
3. Customize components in `apps/templates/includes/`

### Adding New Features
1. Create a new blueprint in `apps/`
2. Add routes in `routes.py`
3. Create templates in `apps/templates/`
4. Register blueprint in `apps/__init__.py`

### Firebase Configuration
1. Update Firebase settings in `credentials/firebase/`
2. Modify authentication flow in `apps/authentication/`
3. Update security rules as needed

## Security Considerations

- Keep Firebase credentials secure
- Never commit .env file
- Use strong SECRET_KEY in production
- Regularly update dependencies
- Implement rate limiting for production
- Enable CSRF protection
- Use HTTPS in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and feature requests, please create an issue in the repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
