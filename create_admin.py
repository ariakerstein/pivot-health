from app import app, db
from models import User
from flask_login import UserMixin

def create_admin_user():
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@pivothealth.ai').first()
        if admin:
            # Update password if user exists
            admin.set_password('AdminPivot2024!')
        else:
            # Create new admin user
            admin = User(
                username='admin',
                email='admin@pivothealth.ai'
            )
            admin.set_password('AdminPivot2024!')
            db.session.add(admin)
        
        db.session.commit()
        print("Admin user created/updated successfully")

if __name__ == '__main__':
    create_admin_user()
