"""
SMC (System Management Component) - Main entry point.
"""

import os

# Import the app factory from SMC_logic
from SMC_Logic import create_app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Run the development server
    port = int(os.environ.get('SMC_PORT', 5001))
    debug = os.environ.get('SMC_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting SMC Service on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
