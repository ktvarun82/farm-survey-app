from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import Base, engine, get_db
from models import FarmSurvey, Tree
from schemas import (
    FarmSurveyCreate, FarmSurveyUpdate, FarmSurvey as FarmSurveySchema,
    TreeCreate, TreeUpdate, Tree as TreeSchema
)

from fastapi.middleware.cors import CORSMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Farm Survey API",
    description="API for managing farm surveys with conflict resolution",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    """Serve the frontend HTML file"""
    return FileResponse("static/index.html")


@app.post("/surveys/", response_model=FarmSurveySchema, status_code=201)
def create_survey(survey: FarmSurveyCreate, db: Session = Depends(get_db)):
    """Create a new farm survey"""
    db_survey = FarmSurvey(
        farmer_name=survey.farmer_name,
        crop_type=survey.crop_type,
        latitude=survey.geo_location.latitude,
        longitude=survey.geo_location.longitude,
        sync_status=survey.sync_status,
        last_updated=datetime.utcnow()
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    
    # Convert to response schema
    return _db_to_schema(db_survey)


@app.get("/surveys/", response_model=List[FarmSurveySchema])
def get_surveys(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all farm surveys"""
    surveys = db.query(FarmSurvey).offset(skip).limit(limit).all()
    return [_db_to_schema(survey, include_trees=True) for survey in surveys]


@app.get("/surveys/{survey_id}", response_model=FarmSurveySchema)
def get_survey(survey_id: int, db: Session = Depends(get_db)):
    """Get a specific farm survey by ID"""
    survey = db.query(FarmSurvey).filter(FarmSurvey.survey_id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return _db_to_schema(survey)


@app.put("/surveys/{survey_id}", response_model=FarmSurveySchema)
def update_survey(
    survey_id: int, 
    survey_update: FarmSurveyUpdate, 
    db: Session = Depends(get_db),
    last_updated: Optional[datetime] = Query(None, description="Last updated timestamp for conflict resolution")
):
    """Update a farm survey with conflict resolution using last_updated timestamp"""
    db_survey = db.query(FarmSurvey).filter(FarmSurvey.survey_id == survey_id).first()
    if not db_survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    # Conflict resolution: check if last_updated matches (if provided)
    if last_updated is not None:
        # Normalize timestamps for comparison (remove microseconds difference)
        if abs((db_survey.last_updated - last_updated).total_seconds()) > 1:
            raise HTTPException(
                status_code=409, 
                detail="Conflict: Survey was modified since last read. Please fetch the latest version and retry."
            )
    
    # Update fields if provided
    if survey_update.farmer_name is not None:
        db_survey.farmer_name = survey_update.farmer_name
    if survey_update.crop_type is not None:
        db_survey.crop_type = survey_update.crop_type
    if survey_update.geo_location is not None:
        db_survey.latitude = survey_update.geo_location.latitude
        db_survey.longitude = survey_update.geo_location.longitude
    if survey_update.sync_status is not None:
        db_survey.sync_status = survey_update.sync_status
    
    db_survey.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_survey)
    
    return _db_to_schema(db_survey)


@app.delete("/surveys/{survey_id}", status_code=204)
def delete_survey(survey_id: int, db: Session = Depends(get_db)):
    """Delete a farm survey (cascades to delete all associated trees)"""
    survey = db.query(FarmSurvey).filter(FarmSurvey.survey_id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    db.delete(survey)
    db.commit()
    return None


# Tree endpoints
@app.post("/surveys/{survey_id}/trees/", response_model=TreeSchema, status_code=201)
def create_tree(survey_id: int, tree: TreeCreate, db: Session = Depends(get_db)):
    """Create a new tree record for a survey"""
    # Verify survey exists
    survey = db.query(FarmSurvey).filter(FarmSurvey.survey_id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    db_tree = Tree(
        survey_id=survey_id,
        species_name=tree.species_name,
        tree_count=tree.tree_count,
        height_avg=tree.height_avg,
        diameter_avg=tree.diameter_avg,
        age_avg=tree.age_avg,
        notes=tree.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_tree)
    db.commit()
    db.refresh(db_tree)
    
    return _db_tree_to_schema(db_tree)


@app.get("/surveys/{survey_id}/trees/", response_model=List[TreeSchema])
def get_trees(survey_id: int, db: Session = Depends(get_db)):
    """Get all trees for a specific survey"""
    # Verify survey exists
    survey = db.query(FarmSurvey).filter(FarmSurvey.survey_id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    trees = db.query(Tree).filter(Tree.survey_id == survey_id).all()
    return [_db_tree_to_schema(tree) for tree in trees]


@app.get("/trees/{tree_id}", response_model=TreeSchema)
def get_tree(tree_id: int, db: Session = Depends(get_db)):
    """Get a specific tree by ID"""
    tree = db.query(Tree).filter(Tree.tree_id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")
    return _db_tree_to_schema(tree)


@app.put("/trees/{tree_id}", response_model=TreeSchema)
def update_tree(tree_id: int, tree_update: TreeUpdate, db: Session = Depends(get_db)):
    """Update a tree record"""
    db_tree = db.query(Tree).filter(Tree.tree_id == tree_id).first()
    if not db_tree:
        raise HTTPException(status_code=404, detail="Tree not found")
    
    # Update fields if provided
    if tree_update.species_name is not None:
        db_tree.species_name = tree_update.species_name
    if tree_update.tree_count is not None:
        db_tree.tree_count = tree_update.tree_count
    if tree_update.height_avg is not None:
        db_tree.height_avg = tree_update.height_avg
    if tree_update.diameter_avg is not None:
        db_tree.diameter_avg = tree_update.diameter_avg
    if tree_update.age_avg is not None:
        db_tree.age_avg = tree_update.age_avg
    if tree_update.notes is not None:
        db_tree.notes = tree_update.notes
    
    db_tree.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_tree)
    
    return _db_tree_to_schema(db_tree)


@app.delete("/trees/{tree_id}", status_code=204)
def delete_tree(tree_id: int, db: Session = Depends(get_db)):
    """Delete a tree record"""
    tree = db.query(Tree).filter(Tree.tree_id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")
    db.delete(tree)
    db.commit()
    return None


def _db_to_schema(db_survey: FarmSurvey, include_trees: bool = True) -> FarmSurveySchema:
    """Helper function to convert database model to Pydantic schema"""
    from schemas import GeoLocation
    
    trees = []
    if include_trees and db_survey.trees:
        trees = [_db_tree_to_schema(tree) for tree in db_survey.trees]
    
    return FarmSurveySchema(
        survey_id=db_survey.survey_id,
        farmer_name=db_survey.farmer_name,
        crop_type=db_survey.crop_type,
        geo_location=GeoLocation(
            latitude=db_survey.latitude,
            longitude=db_survey.longitude
        ),
        sync_status=db_survey.sync_status,
        last_updated=db_survey.last_updated,
        trees=trees
    )


def _db_tree_to_schema(db_tree: Tree) -> TreeSchema:
    """Helper function to convert Tree database model to Pydantic schema"""
    return TreeSchema(
        tree_id=db_tree.tree_id,
        survey_id=db_tree.survey_id,
        species_name=db_tree.species_name,
        tree_count=db_tree.tree_count,
        height_avg=db_tree.height_avg,
        diameter_avg=db_tree.diameter_avg,
        age_avg=db_tree.age_avg,
        notes=db_tree.notes,
        created_at=db_tree.created_at,
        updated_at=db_tree.updated_at
    )

