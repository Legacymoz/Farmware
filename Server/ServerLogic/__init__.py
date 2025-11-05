"""
Basic Flask application factory for Farmware Server.
"""

from flask import Flask
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """
    Application factory function that creates and configures the Flask app.
    
    Returns:
        Flask: Configured Flask application instance
    """
    server_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create Flask app instance
    app = Flask(__name__, 
                template_folder=os.path.join(server_dir, 'templates'),
                static_folder=os.path.join(server_dir, 'static'))
    
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'postgresql://mozart:farmware2025@localhost:5432/farmware_db'
    )

    # Validate critical environment variables
    required_env_vars = ['USSD_CODE', 'SMC_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {missing_vars}")
    

    
    # Enable CORS for all routes
    CORS(app)


    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models so they're registered with SQLAlchemy
    from ServerLogic import models
    
    # Register blueprints
    from ServerLogic.routes import routes_bp
    app.register_blueprint(routes_bp)
    
    #Test database connection
    try:
        # This will test if we can connect to the database
        with app.app_context():
            db.engine.connect()
        print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

    
    return app
