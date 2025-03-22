from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging

from ..database import get_db
from ..models.database_models import FoodLog
from ..models.food import FoodEntry, FoodResponse, FoodAnalysis
from ..services.food_analyzer import FoodAnalyzerService, parse_nutrient_string
from ..services.image_analyzer import analyze_image  # Import your image analysis service

logger = logging.getLogger(__name__)
router = APIRouter()
food_analyzer = FoodAnalyzerService()

@router.post("/analyze", response_model=FoodResponse)
async def analyze_food(food_entry: FoodEntry, db: Session = Depends(get_db)):
    try:
        # Analyze the food
        analysis = await food_analyzer.analyze_food(food_entry.description)
        
        # Create database entry
        db_food_log = FoodLog(
            description=analysis["description"],
            calories=analysis["calories"],
            macronutrients=analysis["macronutrients"],
            micronutrients=analysis["micronutrients"],
            created_at=datetime.utcnow()
        )
        
        # Save to database
        
        db.add(db_food_log)
        db.commit()
        db.refresh(db_food_log)
        
        # Create response
        food_analysis = FoodAnalysis(
            description=analysis["description"],
            calories=analysis["calories"],
            macronutrients=analysis["macronutrients"],
            micronutrients=analysis["micronutrients"],
            timestamp=db_food_log.created_at
        )
        
        return FoodResponse(
            message="Food entry logged successfully",
            entry=food_analysis
        )
    except Exception as e:
        logger.error(f"Error processing food entry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/track/image")
async def track_food_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await image.read()
        
        # Analyze the image to get food information
        # Add await here to properly handle the coroutine
        analysis = await analyze_image(contents)
        
        # Create database entry
        db_food_log = FoodLog(
            description=analysis["description"],
            calories=analysis["calories"],
            macronutrients=analysis["macronutrients"],
            micronutrients=analysis["micronutrients"],
            created_at=datetime.utcnow()
        )
        
        # Save to database
        db.add(db_food_log)
        db.commit()
        db.refresh(db_food_log)
        
        # Create response
        food_analysis = FoodAnalysis(
            description=analysis["description"],
            calories=analysis["calories"],
            macronutrients=analysis["macronutrients"],
            micronutrients=analysis["micronutrients"],
            timestamp=db_food_log.created_at
        )
        
        return {"message": "Image processed and food entry logged successfully", "entry": food_analysis}
    except Exception as e:
        logger.error(f"Error processing food image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/logs", response_model=List[FoodAnalysis])
async def get_food_logs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    logs = db.query(FoodLog).order_by(FoodLog.created_at.desc()).offset(skip).limit(limit).all()
    return [
        FoodAnalysis(
            description=log.description,
            calories=log.calories,
            macronutrients=log.macronutrients,
            micronutrients={
                "vitamins": parse_nutrient_string(log.micronutrients["vitamins"]),
                "minerals": parse_nutrient_string(log.micronutrients["minerals"])
            },
            timestamp=log.created_at
        ) for log in logs
    ]

@router.get("/logs/{log_id}", response_model=FoodAnalysis)
async def get_food_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(FoodLog).filter(FoodLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")
    
    return FoodAnalysis(
        description=log.description,
        calories=log.calories,
        macronutrients=log.macronutrients,
        micronutrients={
            "vitamins": parse_nutrient_string(log.micronutrients["vitamins"]),
            "minerals": parse_nutrient_string(log.micronutrients["minerals"])
        },
        timestamp=log.created_at
    )