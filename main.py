from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

import langchain

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

langchain.debug = True

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

app = FastAPI()

# Initialize LangChain components
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
)

# Define the output schema
response_schemas = [
    ResponseSchema(name="description", description="A cleaned up description of the food"),
    ResponseSchema(name="calories", description="Estimated total calories as a number"),
    ResponseSchema(name="macronutrients", description="Macronutrients breakdown in grams"),
    ResponseSchema(name="micronutrients", description="Key micronutrients and their amounts"),
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# Create the prompt template
prompt_template = ChatPromptTemplate.from_template("""
You are a nutritionist expert that analyzes food descriptions and provides detailed nutritional information.

Analyze the following food description and provide:
1. A cleaned up description
2. Estimated total calories as a number
3. Macronutrients breakdown:
   - Protein (g)
   - Carbohydrates (g)
   - Fat (g)
   - Fiber (g)
4. Key micronutrients (with amounts in mg or mcg):
   - Vitamins (A, B, C, D, etc.)
   - Minerals (Iron, Calcium, etc.)

Food description: {food_description}

{format_instructions}
""")

# In-memory storage (replace with a database in production)
food_logs = []

class FoodEntry(BaseModel):
    description: str
    calories: Optional[float] = None
    timestamp: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

async def analyze_food_text(description: str) -> dict:
    """
    Use LangChain to analyze food description and estimate calories
    """
    try:
        logger.info(f"Analyzing food description: {description}")
        
        # Format the prompt with format instructions
        format_instructions = output_parser.get_format_instructions()
        prompt = prompt_template.format_messages(
            food_description=description,
            format_instructions=format_instructions
        )
        logger.debug(f"Generated prompt: {prompt}")
        
        # Get response from LLM
        logger.info("Sending request to LLM")
        response = await llm.ainvoke(prompt)
        logger.debug(f"Raw LLM response: {response}")
        
        # Parse the response
        result = output_parser.parse(response.content)
        logger.info("Successfully parsed LLM response")
        logger.debug(f"Parsed result: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing food description: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing food description: {str(e)}")

@app.post("/track/text")
async def track_food_text(food_entry: FoodEntry):
    """
    Track calories from natural language description
    Example: "I ate a chicken sandwich with fries"
    """
    try:
        logger.info(f"Processing food entry: {food_entry.description}")
        
        # Analyze the food description using LangChain
        analysis = await analyze_food_text(food_entry.description)
        
        # Update the food entry with analyzed data
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
        logger.debug(f"Stored entry: {entry_dict}")
        
        return {
            "message": "Food entry logged successfully",
            "entry": entry_dict
        }
    except Exception as e:
        logger.error(f"Error processing food entry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/track/image")
async def track_food_image(image: UploadFile = File(...)):
    """
    Track calories from an uploaded image of a plate
    """
    try:
        # Here you would integrate with an image recognition service
        # For now, we'll just return a placeholder response
        contents = await image.read()
        
        # Placeholder for image processing result
        food_entry = {
            "description": "Food from image",
            "calories": 0,
            "timestamp": None
        }
        
        food_logs.append(food_entry)
        return {"message": "Image processed successfully", "entry": food_entry}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/logs")
async def get_food_logs():
    """
    Retrieve all food tracking logs
    """
    return {"logs": food_logs}
