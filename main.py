from app import app
from flask import Flask

if __name__ == "__main__":
    # Ensure we're using port 5000 explicitly
    port = 5000
    app.run(host="0.0.0.0", port=port, debug=True)
