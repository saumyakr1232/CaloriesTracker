from pydantic import BaseModel
from typing import Optional, Dict

class FoodEntry(BaseModel):
    description: str
    calories: Optional[float] = None
    timestamp: Optional[str] = None
    macronutrients: Optional[Dict[str, float]] = None
    micronutrients: Optional[Dict[str, str]] = None

class FoodResponse(BaseModel):
    message: str
    entry: FoodEntry 