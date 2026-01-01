"""
Pytest configuration and fixtures for testing the Farm Survey application
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile

from database import Base, get_db
from models import FarmSurvey
from main import app


# Create a temporary database for testing
TEST_DB_FILE = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
TEST_DB_PATH = TEST_DB_FILE.name
TEST_DB_FILE.close()

# Create test database engine
TEST_SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_survey_data():
    """Sample survey data for testing"""
    return {
        "farmer_name": "John Doe",
        "crop_type": "Wheat",
        "geo_location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "sync_status": False
    }


@pytest.fixture
def sample_survey_update_data():
    """Sample survey update data for testing"""
    return {
        "farmer_name": "Jane Doe",
        "crop_type": "Corn",
        "geo_location": {
            "latitude": 41.8781,
            "longitude": -87.6298
        },
        "sync_status": True
    }


def pytest_sessionfinish(session, exitstatus):
    """Cleanup test database file after all tests"""
    try:
        if os.path.exists(TEST_DB_PATH):
            os.unlink(TEST_DB_PATH)
    except Exception:
        pass

