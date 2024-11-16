from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Base class for database models
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    instagram_user_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(50), nullable=False)
    access_token = Column(Text, nullable=False)
    token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reply_tone = Column(String(20), default="positive") 

# Initialize the database connection
DATABASE_URL = "sqlite:///replyforme.db"  # SQLite URL (change to PostgreSQL for production)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized!")
