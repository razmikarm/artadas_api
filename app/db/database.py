from sqlmodel import SQLModel, create_engine, Session

# Database URL
DATABASE_URL = "sqlite:///./test.db"

# Create database engine
engine = create_engine(DATABASE_URL)

# Initialize the database
def init_db():
    SQLModel.metadata.create_all(engine)

# Dependency to get a database session
def get_session():
    with Session(engine) as session:
        yield session
