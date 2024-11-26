import os
import sys
from app import app, init_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_server():
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        
        # Get port from environment variables, with Replit-specific configuration
        port = int(os.environ.get('PORT', os.environ.get('REPLIT_PORT', 5000)))
        logger.info(f"Starting server on port {port}")
        
        # Run the application
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,  # Disable reloader in production
            threaded=True  # Enable threading for better concurrency
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
