from fastapi import APIRouter, File, UploadFile, HTTPException
from datetime import datetime
import logging
from app.models.food import FoodEntry, FoodResponse
from app.services.food_analyzer import FoodAnalyzerService

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage (replace with a database in production)
food_logs = []

food_analyzer = FoodAnalyzerService()

@router.post("/track/text", response_model=FoodResponse)
async def track_food_text(food_entry: FoodEntry):
    try:
        logger.info(f"Processing food entry: {food_entry.description}")
        
        analysis = await food_analyzer.analyze_food(food_entry.description)
        
        entry_dict = food_entry.dict()
        entry_dict.update({
            "description": analysis["description"],
            "calories": float(analysis["calories"]),
            "macronutrients": analysis["macronutrients"],
            "micronutrients": analysis["micronutrients"],
            "timestamp": datetime.now().isoformat()
        })
        
        food_logs.append(entry_dict)
        logger.info("Food entry successfully logged")
        
        return FoodResponse(
            message="Food entry logged successfully",
            entry=entry_dict
        )
    except Exception as e:
        logger.error(f"Error processing food entry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/track/image")
async def track_food_image(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        food_entry = {
            "description": "Food from image",
            "calories": 0,
            "timestamp": None
        }
        food_logs.append(food_entry)
        return {"message": "Image processed successfully", "entry": food_entry}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/logs")
async def get_food_logs():
    return {"logs": food_logs} 