"""
Tests for database models
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from models import FarmSurvey
from conftest import db_session


def test_farm_survey_creation(db_session: Session):
    """Test creating a FarmSurvey instance"""
    survey = FarmSurvey(
        farmer_name="Test Farmer",
        crop_type="Wheat",
        latitude=40.7128,
        longitude=-74.0060,
        sync_status=False
    )
    
    db_session.add(survey)
    db_session.commit()
    db_session.refresh(survey)
    
    assert survey.survey_id is not None
    assert survey.farmer_name == "Test Farmer"
    assert survey.crop_type == "Wheat"
    assert survey.latitude == 40.7128
    assert survey.longitude == -74.0060
    assert survey.sync_status is False
    assert survey.last_updated is not None
    assert isinstance(survey.last_updated, datetime)


def test_farm_survey_defaults(db_session: Session):
    """Test that default values are set correctly"""
    survey = FarmSurvey(
        farmer_name="Test Farmer",
        crop_type="Corn",
        latitude=0.0,
        longitude=0.0
        # sync_status not provided, should default to False
    )
    
    db_session.add(survey)
    db_session.commit()
    
    assert survey.sync_status is False


def test_farm_survey_last_updated_auto_update(db_session: Session):
    """Test that last_updated is automatically updated on modification"""
    survey = FarmSurvey(
        farmer_name="Test Farmer",
        crop_type="Wheat",
        latitude=40.7128,
        longitude=-74.0060
    )
    
    db_session.add(survey)
    db_session.commit()
    db_session.refresh(survey)
    
    original_timestamp = survey.last_updated
    
    # Update the survey
    import time
    time.sleep(1)  # Ensure timestamp difference
    survey.crop_type = "Corn"
    db_session.commit()
    db_session.refresh(survey)
    
    assert survey.last_updated >= original_timestamp


def test_farm_survey_required_fields(db_session: Session):
    """Test that required fields cannot be None"""
    # Test farmer_name is required
    with pytest.raises(Exception):
        survey = FarmSurvey(
            crop_type="Wheat",
            latitude=40.7128,
            longitude=-74.0060
        )
        db_session.add(survey)
        db_session.commit()
    
    db_session.rollback()
    
    # Test crop_type is required
    with pytest.raises(Exception):
        survey = FarmSurvey(
            farmer_name="Test",
            latitude=40.7128,
            longitude=-74.0060
        )
        db_session.add(survey)
        db_session.commit()


def test_multiple_surveys(db_session: Session):
    """Test creating multiple surveys"""
    survey1 = FarmSurvey(
        farmer_name="Farmer 1",
        crop_type="Wheat",
        latitude=40.7128,
        longitude=-74.0060
    )
    
    survey2 = FarmSurvey(
        farmer_name="Farmer 2",
        crop_type="Corn",
        latitude=41.8781,
        longitude=-87.6298,
        sync_status=True
    )
    
    db_session.add_all([survey1, survey2])
    db_session.commit()
    
    surveys = db_session.query(FarmSurvey).all()
    assert len(surveys) == 2
    assert surveys[0].survey_id != surveys[1].survey_id
    assert surveys[0].farmer_name == "Farmer 1"
    assert surveys[1].farmer_name == "Farmer 2"

