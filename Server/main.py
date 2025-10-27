"""
Farmware Server - Main entry point.
"""
import os

# Import the app factory from ServerLogic
from ServerLogic import create_app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Run the development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Farmware Server on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
