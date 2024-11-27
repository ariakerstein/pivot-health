import os
import sys
import socket
from app import app, init_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return False
        except socket.error:
            return True

def find_available_port(start_port=5000, max_port=5100):
    port = start_port
    while port <= max_port:
        if not is_port_in_use(port):
            return port
        port += 1
    raise RuntimeError(f"No available ports found between {start_port} and {max_port}")

def start_server():
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        
        # Get port from environment variables, with Replit-specific configuration
        preferred_port = int(os.environ.get('PORT', os.environ.get('REPLIT_PORT', 5000)))
        
        # Find an available port
        port = find_available_port(preferred_port)
        logger.info(f"Starting server on port {port}")
        
        # Production configuration
        app.config['ENV'] = 'production'
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        # Start the server
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
