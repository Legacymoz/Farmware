"""
Basic Flask application factory for SMC (System Management Component).
"""

from flask import Flask
from flask_cors import CORS
import os



def create_app():
    """
    Application factory function that creates and configures the SMC Flask app.
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask app instance
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SMC_SECRET_KEY', 'smc-dev-secret-key')
    app.config['DEBUG'] = os.environ.get('SMC_DEBUG', 'False').lower() == 'true'
    
    # Enable CORS for all routes
    CORS(app)

    # Register blueprints
    from SMC_Logic.routes import smc_routes_bp
    app.register_blueprint(smc_routes_bp)
    
    return app