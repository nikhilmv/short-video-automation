import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.core.security import hash_password

def seed_users():
    # Make sure all tables are created (useful if not using migrations yet)
    # Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if the user already exists
        existing_user = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_user:
            print("User admin@example.com already exists!")
            return

        # Create dummy admin user
        hashed_pw = hash_password("password123")
        admin_user = User(
            name="Admin User",
            email="admin@example.com",
            password=hashed_pw,
            # If you add role and status to your User model later, uncomment these:
            # role="Admin",
            # status="Active"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Successfully created admin user with ID: {admin_user.id}")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
