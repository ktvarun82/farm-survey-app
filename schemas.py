from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class GeoLocation(BaseModel):
    """Geographic location with latitude and longitude"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate (-90 to 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate (-180 to 180)")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }


class FarmSurveyBase(BaseModel):
    """Base schema for FarmSurvey with common fields"""
    farmer_name: str = Field(..., min_length=1, description="Name of the farmer")
    crop_type: str = Field(..., min_length=1, description="Type of crop")
    geo_location: GeoLocation = Field(..., description="Geographic location (latitude and longitude)")
    sync_status: bool = Field(default=False, description="Synchronization status")


class FarmSurveyCreate(FarmSurveyBase):
    """Schema for creating a new FarmSurvey"""
    pass


class FarmSurveyUpdate(BaseModel):
    """Schema for updating an existing FarmSurvey"""
    farmer_name: Optional[str] = Field(None, min_length=1, description="Name of the farmer")
    crop_type: Optional[str] = Field(None, min_length=1, description="Type of crop")
    geo_location: Optional[GeoLocation] = Field(None, description="Geographic location")
    sync_status: Optional[bool] = Field(None, description="Synchronization status")


class TreeBase(BaseModel):
    """Base schema for Tree with common fields"""
    species_name: str = Field(..., min_length=1, description="Name of the tree species")
    tree_count: int = Field(..., gt=0, description="Number of trees of this species")
    height_avg: Optional[float] = Field(None, ge=0, description="Average height in meters")
    diameter_avg: Optional[float] = Field(None, ge=0, description="Average diameter in centimeters")
    age_avg: Optional[int] = Field(None, ge=0, description="Average age in years")
    notes: Optional[str] = Field(None, description="Additional notes about the trees")


class TreeCreate(TreeBase):
    """Schema for creating a new Tree"""
    pass


class TreeUpdate(BaseModel):
    """Schema for updating an existing Tree"""
    species_name: Optional[str] = Field(None, min_length=1, description="Name of the tree species")
    tree_count: Optional[int] = Field(None, gt=0, description="Number of trees of this species")
    height_avg: Optional[float] = Field(None, ge=0, description="Average height in meters")
    diameter_avg: Optional[float] = Field(None, ge=0, description="Average diameter in centimeters")
    age_avg: Optional[int] = Field(None, ge=0, description="Average age in years")
    notes: Optional[str] = Field(None, description="Additional notes about the trees")


class Tree(TreeBase):
    """Schema for Tree response"""
    tree_id: int = Field(..., description="Unique identifier for the tree record")
    survey_id: int = Field(..., description="Foreign key to the survey")
    created_at: datetime = Field(..., description="Timestamp when tree record was created")
    updated_at: datetime = Field(..., description="Timestamp when tree record was last updated")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "tree_id": 1,
                "survey_id": 1,
                "species_name": "Oak",
                "tree_count": 25,
                "height_avg": 12.5,
                "diameter_avg": 45.0,
                "age_avg": 15,
                "notes": "Mature trees in good condition",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class FarmSurvey(FarmSurveyBase):
    """Schema for FarmSurvey response"""
    survey_id: int = Field(..., description="Unique identifier for the survey")
    last_updated: datetime = Field(..., description="Timestamp of last update for conflict resolution")
    trees: Optional[List[Tree]] = Field(default=[], description="List of trees associated with this survey")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "survey_id": 1,
                "farmer_name": "John Doe",
                "crop_type": "Wheat",
                "geo_location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "sync_status": False,
                "last_updated": "2024-01-15T10:30:00",
                "trees": []
            }
        }

