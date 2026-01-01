"""
Tests for API endpoints
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from conftest import client, sample_survey_data, sample_survey_update_data


def test_read_root(client: TestClient):
    """Test root endpoint serves HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Farm Survey Management" in response.text


def test_create_survey_success(client: TestClient, sample_survey_data):
    """Test creating a survey successfully"""
    response = client.post("/surveys/", json=sample_survey_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["survey_id"] is not None
    assert data["farmer_name"] == sample_survey_data["farmer_name"]
    assert data["crop_type"] == sample_survey_data["crop_type"]
    assert data["geo_location"]["latitude"] == sample_survey_data["geo_location"]["latitude"]
    assert data["geo_location"]["longitude"] == sample_survey_data["geo_location"]["longitude"]
    assert data["sync_status"] == sample_survey_data["sync_status"]
    assert "last_updated" in data


def test_create_survey_missing_fields(client: TestClient):
    """Test creating survey with missing required fields"""
    incomplete_data = {
        "farmer_name": "John Doe"
        # Missing crop_type and geo_location
    }
    response = client.post("/surveys/", json=incomplete_data)
    assert response.status_code == 422  # Validation error


def test_create_survey_invalid_geo_location(client: TestClient):
    """Test creating survey with invalid coordinates"""
    invalid_data = {
        "farmer_name": "John Doe",
        "crop_type": "Wheat",
        "geo_location": {
            "latitude": 100.0,  # Invalid (should be -90 to 90)
            "longitude": -74.0060
        }
    }
    response = client.post("/surveys/", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_get_surveys_empty(client: TestClient):
    """Test getting surveys when none exist"""
    response = client.get("/surveys/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_surveys_with_data(client: TestClient, sample_survey_data):
    """Test getting surveys when they exist"""
    # Create a survey
    create_response = client.post("/surveys/", json=sample_survey_data)
    assert create_response.status_code == 201
    
    # Get all surveys
    response = client.get("/surveys/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["farmer_name"] == sample_survey_data["farmer_name"]


def test_get_surveys_pagination(client: TestClient, sample_survey_data):
    """Test pagination parameters"""
    # Create multiple surveys
    for i in range(5):
        data = sample_survey_data.copy()
        data["farmer_name"] = f"Farmer {i}"
        client.post("/surveys/", json=data)
    
    # Test limit
    response = client.get("/surveys/?limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Test skip
    response = client.get("/surveys/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_survey_by_id_success(client: TestClient, sample_survey_data):
    """Test getting a survey by ID"""
    # Create a survey
    create_response = client.post("/surveys/", json=sample_survey_data)
    survey_id = create_response.json()["survey_id"]
    
    # Get the survey
    response = client.get(f"/surveys/{survey_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["survey_id"] == survey_id
    assert data["farmer_name"] == sample_survey_data["farmer_name"]


def test_get_survey_by_id_not_found(client: TestClient):
    """Test getting a non-existent survey"""
    response = client.get("/surveys/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_survey_success(client: TestClient, sample_survey_data, sample_survey_update_data):
    """Test updating a survey successfully"""
    # Create a survey
    create_response = client.post("/surveys/", json=sample_survey_data)
    survey_id = create_response.json()["survey_id"]
    last_updated = create_response.json()["last_updated"]
    
    # Update the survey
    response = client.put(
        f"/surveys/{survey_id}",
        json=sample_survey_update_data,
        params={"last_updated": last_updated}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["farmer_name"] == sample_survey_update_data["farmer_name"]
    assert data["crop_type"] == sample_survey_update_data["crop_type"]
    assert data["sync_status"] == sample_survey_update_data["sync_status"]


def test_update_survey_partial(client: TestClient, sample_survey_data):
    """Test partial update of a survey"""
    # Create a survey
    create_response = client.post("/surveys/", json=sample_survey_data)
    survey_id = create_response.json()["survey_id"]
    last_updated = create_response.json()["last_updated"]
    
    # Update only farmer_name
    update_data = {"farmer_name": "Updated Name"}
    response = client.put(
        f"/surveys/{survey_id}",
        json=update_data,
        params={"last_updated": last_updated}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["farmer_name"] == "Updated Name"
    assert data["crop_type"] == sample_survey_data["crop_type"]  # Unchanged


def test_update_survey_conflict_resolution(client: TestClient, sample_survey_data):
    """Test conflict resolution with last_updated timestamp"""
    # Create a survey
    create_response = client.post("/surveys/", json=sample_survey_data)
    survey_id = create_response.json()["survey_id"]
    original_last_updated = create_response.json()["last_updated"]
    
    # Simulate another user updating the survey first
    fake_old_timestamp = (datetime.fromisoformat(original_last_updated.replace('Z', '+00:00')) - timedelta(hours=1)).isoformat()
    
    # Try to update with old timestamp
    response = client.put(
        f"/surveys/{survey_id}",
        json={"farmer_name": "Updated Name"},
        params={"last_updated": fake_old_timestamp}
    )
    assert response.status_code == 409  # Conflict
    assert "conflict" in response.json()["detail"].lower()


def test_update_survey_not_found(client: TestClient):
    """Test updating a non-existent survey"""
    response = client.put(
        "/surveys/99999",
        json={"farmer_name": "Updated Name"}
    )
    assert response.status_code == 404


def test_delete_survey_success(client: TestClient, sample_survey_data):
    """Test deleting a survey successfully"""
    # Create a survey
    create_response = client.post("/surveys/", json=sample_survey_data)
    survey_id = create_response.json()["survey_id"]
    
    # Delete the survey
    response = client.delete(f"/surveys/{survey_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/surveys/{survey_id}")
    assert get_response.status_code == 404


def test_delete_survey_not_found(client: TestClient):
    """Test deleting a non-existent survey"""
    response = client.delete("/surveys/99999")
    assert response.status_code == 404


def test_crud_workflow(client: TestClient, sample_survey_data, sample_survey_update_data):
    """Test complete CRUD workflow"""
    # Create
    create_response = client.post("/surveys/", json=sample_survey_data)
    assert create_response.status_code == 201
    survey_id = create_response.json()["survey_id"]
    last_updated = create_response.json()["last_updated"]
    
    # Read
    get_response = client.get(f"/surveys/{survey_id}")
    assert get_response.status_code == 200
    assert get_response.json()["survey_id"] == survey_id
    
    # Update
    update_response = client.put(
        f"/surveys/{survey_id}",
        json=sample_survey_update_data,
        params={"last_updated": last_updated}
    )
    assert update_response.status_code == 200
    assert update_response.json()["farmer_name"] == sample_survey_update_data["farmer_name"]
    
    # Delete
    delete_response = client.delete(f"/surveys/{survey_id}")
    assert delete_response.status_code == 204
    
    # Verify deletion
    get_after_delete = client.get(f"/surveys/{survey_id}")
    assert get_after_delete.status_code == 404

