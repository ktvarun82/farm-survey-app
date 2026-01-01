from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class FarmSurvey(Base):
    __tablename__ = "farm_surveys"

    survey_id = Column(Integer, primary_key=True, index=True)
    farmer_name = Column(String, nullable=False, index=True)
    crop_type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    sync_status = Column(Boolean, default=False, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to trees
    trees = relationship("Tree", back_populates="survey", cascade="all, delete-orphan")


class Tree(Base):
    __tablename__ = "trees"

    tree_id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("farm_surveys.survey_id", ondelete="CASCADE"), nullable=False, index=True)
    species_name = Column(String, nullable=False, index=True)
    tree_count = Column(Integer, nullable=False)
    height_avg = Column(Float, nullable=True, comment="Average height in meters")
    diameter_avg = Column(Float, nullable=True, comment="Average diameter in centimeters")
    age_avg = Column(Integer, nullable=True, comment="Average age in years")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to survey
    survey = relationship("FarmSurvey", back_populates="trees")


