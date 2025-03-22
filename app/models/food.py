from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class Macronutrients(BaseModel):
    protein: float
    carbohydrates: float
    fat: float
    fiber: float

class Micronutrients(BaseModel):
    vitamins: Dict[str, str]
    minerals: Dict[str, str]

class FoodEntry(BaseModel):
    description: str

class FoodAnalysis(BaseModel):
    description: str
    calories: float
    macronutrients: Macronutrients
    micronutrients: Micronutrients
    timestamp: Optional[datetime] = None

class FoodResponse(BaseModel):
    message: str
    entry: FoodAnalysis 