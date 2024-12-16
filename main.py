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

def find_available_port(start_port=5000, max_port=9000):
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
        if os.environ.get('PRODUCTION'):
            # Use gunicorn in production
            import gunicorn.app.base
            
            class StandaloneApplication(gunicorn.app.base.BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()

                def load_config(self):
                    for key, value in self.options.items():
                        self.cfg.set(key.lower(), value)

                def load(self):
                    return self.application
            
            options = {
                'bind': f'0.0.0.0:{port}',
                'workers': 4,
                'worker_class': 'sync',
                'timeout': 120,
                'keepalive': 5,
                'max_requests': 1000,
                'max_requests_jitter': 50,
                'preload_app': True,
                'worker_connections': 1000
            }
            
            # Add SSL configuration if certificates are available
            ssl_cert = os.environ.get('SSL_CERT_PATH')
            ssl_key = os.environ.get('SSL_KEY_PATH')
            if ssl_cert and ssl_key and os.path.exists(ssl_cert) and os.path.exists(ssl_key):
                options.update({
                    'certfile': ssl_cert,
                    'keyfile': ssl_key,
                    'ssl_version': 'TLS',
                    'ciphers': 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384'
                })
            StandaloneApplication(app, options).run()
        else:
            # Use Flask's development server
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
