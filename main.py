from app import app, init_db

if __name__ == "__main__":
    try:
        init_db()  # Initialize database before starting server
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
