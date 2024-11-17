from src.database import Base, engine

# Create all tables in the database
Base.metadata.create_all(engine)
print("Database initialized with updated schema.")
