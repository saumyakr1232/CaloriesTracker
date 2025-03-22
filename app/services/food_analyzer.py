import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from fastapi import HTTPException
import re
from typing import Dict
from pprint import pprint

logger = logging.getLogger(__name__)

def clean_number(value: str | int | float) -> float:
    """Remove units and convert string to float."""
    if not isinstance(value, str):
        return value
    
    # Remove any non-numeric characters except dots and commas
    number_str = re.sub(r'[^0-9.,]', '', value)
    # Replace comma with dot for proper float conversion
    number_str = number_str.replace(',', '.')
    return float(number_str)

def parse_nutrient_string(nutrient_str: str) -> Dict[str, str]:
    """Convert nutrient string into dictionary format"""
    if isinstance(nutrient_str, dict):
        return nutrient_str
    
    result = {}
    # Split by comma and clean up each entry
    pairs = [pair.strip() for pair in nutrient_str.split(',')]
    for pair in pairs:
        if ':' in pair:
            key, value = pair.split(':', 1)
            result[key.strip()] = value.strip()
    return result

class FoodAnalyzerService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
        )
        
        self.response_schemas = [
            ResponseSchema(name="description", description="A cleaned up description of the food"),
            ResponseSchema(name="calories", description="Estimated total calories as a number"),
            ResponseSchema(name="macronutrients", description="Macronutrients breakdown in grams"),
            ResponseSchema(name="micronutrients", description="Key micronutrients like Vitamins and Minerals and their amounts", type="dict"),
        ]
        
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        
        self.prompt_template = ChatPromptTemplate.from_template("""
            You are a nutritionist expert that analyzes food descriptions and provides detailed nutritional information.

            Analyze the following food description and provide:
            1. A cleaned up description
            2. Estimated total calories as a number
            3. Macronutrients breakdown in grams:
               - Protein
               - Carbohydrates
               - Fat
               - Fiber
            4. Key micronutrients (with amounts in mg or mcg):
               - Vitamins 
                 - Vitamin A
                 - Vitamin B
                 - etc
               - Minerals 
                 - Iron
                 - Calcium
                 - etc

            Food description: {food_description}

            {format_instructions}
        """)

    async def analyze_food(self, description: str) -> dict:
        try:
            logger.info(f"Analyzing food description: {description}")
            
            format_instructions = self.output_parser.get_format_instructions()
            prompt = self.prompt_template.format_messages(
                food_description=description,
                format_instructions=format_instructions
            )
            logger.debug(f"Generated prompt: {prompt}")
            
            response = await self.llm.ainvoke(prompt)
            logger.debug(f"Raw LLM response: {response}")
            
            raw_result = self.output_parser.parse(response.content)
            logger.info("Successfully parsed LLM response")
            logger.debug(f"Parsed result: {raw_result}")

            print('********************')
            pprint(raw_result)
            
            print('********************')
            
            # Clean and structure the response
            cleaned_result = {
                "description": raw_result["description"],
                "calories": clean_number(raw_result["calories"]),
                "macronutrients": {
                    "protein": clean_number(raw_result["macronutrients"]["Protein"]),
                    "carbohydrates": clean_number(raw_result["macronutrients"]["Carbohydrates"]),
                    "fat": clean_number(raw_result["macronutrients"]["Fat"]),
                    "fiber": clean_number(raw_result["macronutrients"]["Fiber"])
                },
                "micronutrients": {
                    "vitamins": parse_nutrient_string(raw_result["micronutrients"]["Vitamins"]),
                    "minerals": parse_nutrient_string(raw_result["micronutrients"]["Minerals"])
                }
            }
            
            logger.debug(f"Cleaned result: {cleaned_result}")
            return cleaned_result
        except Exception as e:
            logger.error(f"Error analyzing food description: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error analyzing food description: {str(e)}") 