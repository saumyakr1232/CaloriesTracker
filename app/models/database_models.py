from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from ..database import Base

class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    calories = Column(Float)
    macronutrients = Column(JSON)
    micronutrients = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow) 