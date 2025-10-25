# list_users.py
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User

def list_registered_users():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            print(f"Email: {user.email}")
    finally:
        db.close()

if __name__ == "__main__":
    list_registered_users()
