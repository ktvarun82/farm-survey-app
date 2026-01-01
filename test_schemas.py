"""
Tests for Pydantic schemas
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from schemas import (
    GeoLocation,
    FarmSurveyBase,
    FarmSurveyCreate,
    FarmSurveyUpdate,
    FarmSurvey
)


def test_geo_location_valid():
    """Test valid GeoLocation creation"""
    location = GeoLocation(latitude=40.7128, longitude=-74.0060)
    assert location.latitude == 40.7128
    assert location.longitude == -74.0060


def test_geo_location_latitude_range():
    """Test latitude range validation"""
    # Valid latitude
    location = GeoLocation(latitude=90.0, longitude=0.0)
    assert location.latitude == 90.0
    
    # Invalid latitude (too high)
    with pytest.raises(ValidationError):
        GeoLocation(latitude=91.0, longitude=0.0)
    
    # Invalid latitude (too low)
    with pytest.raises(ValidationError):
        GeoLocation(latitude=-91.0, longitude=0.0)


def test_geo_location_longitude_range():
    """Test longitude range validation"""
    # Valid longitude
    location = GeoLocation(latitude=0.0, longitude=180.0)
    assert location.longitude == 180.0
    
    # Invalid longitude (too high)
    with pytest.raises(ValidationError):
        GeoLocation(latitude=0.0, longitude=181.0)
    
    # Invalid longitude (too low)
    with pytest.raises(ValidationError):
        GeoLocation(latitude=0.0, longitude=-181.0)


def test_farm_survey_create_valid():
    """Test valid FarmSurveyCreate"""
    survey = FarmSurveyCreate(
        farmer_name="John Doe",
        crop_type="Wheat",
        geo_location=GeoLocation(latitude=40.7128, longitude=-74.0060),
        sync_status=False
    )
    assert survey.farmer_name == "John Doe"
    assert survey.crop_type == "Wheat"
    assert survey.sync_status is False


def test_farm_survey_create_defaults():
    """Test FarmSurveyCreate with default sync_status"""
    survey = FarmSurveyCreate(
        farmer_name="John Doe",
        crop_type="Wheat",
        geo_location=GeoLocation(latitude=40.7128, longitude=-74.0060)
    )
    assert survey.sync_status is False


def test_farm_survey_create_required_fields():
    """Test that required fields are enforced"""
    with pytest.raises(ValidationError):
        FarmSurveyCreate(
            crop_type="Wheat",
            geo_location=GeoLocation(latitude=40.7128, longitude=-74.0060)
        )


def test_farm_survey_update_partial():
    """Test FarmSurveyUpdate with partial fields"""
    # All fields optional
    update1 = FarmSurveyUpdate()
    assert update1.farmer_name is None
    
    # Update only farmer_name
    update2 = FarmSurveyUpdate(farmer_name="Jane Doe")
    assert update2.farmer_name == "Jane Doe"
    assert update2.crop_type is None
    
    # Update multiple fields
    update3 = FarmSurveyUpdate(
        farmer_name="Jane Doe",
        sync_status=True
    )
    assert update3.farmer_name == "Jane Doe"
    assert update3.sync_status is True
    assert update3.crop_type is None


def test_farm_survey_response():
    """Test FarmSurvey response schema"""
    survey = FarmSurvey(
        survey_id=1,
        farmer_name="John Doe",
        crop_type="Wheat",
        geo_location=GeoLocation(latitude=40.7128, longitude=-74.0060),
        sync_status=False,
        last_updated=datetime.now()
    )
    assert survey.survey_id == 1
    assert survey.farmer_name == "John Doe"
    assert isinstance(survey.last_updated, datetime)

