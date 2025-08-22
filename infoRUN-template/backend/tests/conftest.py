import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.core.config import settings

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    # Clean up
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(db_engine):
    """Create test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Create test client with database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "login": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role_id": 3  # Student role
    }


@pytest.fixture
def test_subject_data():
    """Sample subject data for testing."""
    return {
        "name": "Mathematics",
        "description": "Advanced mathematics course"
    }


@pytest.fixture
def test_task_data():
    """Sample task data for testing."""
    return {
        "task_number": 1,
        "task_title": "Algebra Basics",
        "subject_id": 1
    }


@pytest.fixture
def test_subtask_data():
    """Sample subtask data for testing."""
    return {
        "task_id": 1,
        "subtask_number": 1,
        "description": "Solve the equation: 2x + 3 = 7",
        "answer": "2"
    }


@pytest.fixture
def auth_headers():
    """Get authentication headers for testing."""
    # This would be implemented with actual JWT token generation
    return {"Authorization": "Bearer test-token"}


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_user(db_session, **kwargs):
        """Create a test user."""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        user_data = {
            "Login": "testuser",
            "Email": "test@example.com",
            "Password": get_password_hash("testpassword123"),
            "First_Name": "Test",
            "Last_Name": "User",
            "RoleID": 3,
            "IsActive": True,
            "IsConfirmed": True
        }
        user_data.update(kwargs)
        
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @staticmethod
    def create_subject(db_session, **kwargs):
        """Create a test subject."""
        from app.models.subject import Subject
        
        subject_data = {
            "Name": "Mathematics",
            "Description": "Advanced mathematics course"
        }
        subject_data.update(kwargs)
        
        subject = Subject(**subject_data)
        db_session.add(subject)
        db_session.commit()
        db_session.refresh(subject)
        return subject
    
    @staticmethod
    def create_task(db_session, **kwargs):
        """Create a test task."""
        from app.models.task import Task
        
        task_data = {
            "TaskNumber": 1,
            "TaskTitle": "Algebra Basics",
            "SubjectID": 1
        }
        task_data.update(kwargs)
        
        task = Task(**task_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task
    
    @staticmethod
    def create_subtask(db_session, **kwargs):
        """Create a test subtask."""
        from app.models.task import SubTask
        
        subtask_data = {
            "TaskID": 1,
            "SubTaskNumber": 1,
            "Description": "Solve the equation: 2x + 3 = 7",
            "Answer": "2"
        }
        subtask_data.update(kwargs)
        
        subtask = SubTask(**subtask_data)
        db_session.add(subtask)
        db_session.commit()
        db_session.refresh(subtask)
        return subtask


@pytest.fixture
def factory(db_session):
    """Get test data factory."""
    return TestDataFactory
