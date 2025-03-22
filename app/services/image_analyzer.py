import logging
import base64
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from fastapi import HTTPException
from typing import Dict, Any

from .food_analyzer import clean_number, parse_nutrient_string

logger = logging.getLogger(__name__)

def encode_image(image_bytes):
    """Encode image bytes to base64 string for API consumption"""
    return base64.b64encode(image_bytes).decode('utf-8')

class ImageAnalyzerService:
    def __init__(self):
        self.vision_model = ChatOpenAI(
            model_name="gpt-4o-mini",  # Using a model with vision capabilities
            temperature=0.7,
        )
        
        self.response_schemas = [
            ResponseSchema(name="description", description="A detailed description of the food in the image"),
            ResponseSchema(name="calories", description="Estimated total calories as a number"),
            ResponseSchema(name="macronutrients", description="Macronutrients breakdown in grams"),
            ResponseSchema(name="micronutrients", description="Key micronutrients like Vitamins and Minerals and their amounts", type="dict"),
        ]
        
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        
        # Modified to use a simpler prompt template
        self.system_prompt = """
        You are a nutritionist expert that analyzes food images and provides detailed nutritional information.
        
        Analyze the food in the image and provide:
        1. A detailed description of the food
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
             
        {format_instructions}
        """

    async def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze an image of food and extract nutritional information
        
        Args:
            image_bytes: Raw bytes of the uploaded image
            
        Returns:
            Dictionary containing food description and nutritional information
        """
        try:
            logger.info("Analyzing food image")
            
            # Encode the image to base64
            base64_image = encode_image(image_bytes)
            
            # Format instructions for the output parser
            format_instructions = self.output_parser.get_format_instructions()
            
            # Create messages directly instead of using the template
            messages = [
                {"role": "system", "content": self.system_prompt.format(format_instructions=format_instructions)},
                {"role": "user", "content": [
                    {"type": "text", "text": "Analyze this food image"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ]
            
            logger.debug("Sending image to vision model")
            # Use the client directly with the properly formatted messages
            response = await self.vision_model.agenerate([messages])
            response_message = response.generations[0][0].text
            logger.debug("Raw vision model response received")
            
            raw_result = self.output_parser.parse(response_message)
            logger.info("Successfully parsed vision model response")
            
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
            logger.error(f"Error analyzing food image: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error analyzing food image: {str(e)}")

# Create a singleton instance for use in routes
image_analyzer = ImageAnalyzerService()

# Function to maintain backward compatibility with existing code
async def analyze_image(image_bytes: bytes) -> Dict[str, Any]:
    """Wrapper function for backward compatibility"""
    return await image_analyzer.analyze_image(image_bytes)