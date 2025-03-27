import logging
import base64
import json
from openai import OpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from fastapi import HTTPException
from typing import Dict, Any

from .food_analyzer import clean_number, parse_nutrient_string
from .food_analyzer import FoodAnalyzerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def encode_image(image_bytes):
    """Encode image bytes to base64 string for API consumption"""
    return base64.b64encode(image_bytes).decode('utf-8')

class ImageAnalyzerService:
    def __init__(self):
        # Initialize the OpenAI client directly
        self.client = OpenAI()
        self.food_analyzer = FoodAnalyzerService()
        
        # self.response_schemas = [
        #     ResponseSchema(name="description", description="A detailed description of the food in the image"),
        #     ResponseSchema(name="calories", description="Estimated total calories as a number"),
        #     ResponseSchema(name="macronutrients", description="Macronutrients breakdown in grams"),
        #     ResponseSchema(name="micronutrients", description="Key micronutrients like Vitamins and Minerals and their amounts", type="dict"),
        # ]
        
        # self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        
        # System prompt for the vision model
        self.system_prompt = """
        Analyzes food images and provides detailed contents of the plate.
        """

    async def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        try:
            logger.info("Starting image analysis process")
            
            # Encode the image to base64
            base64_image = encode_image(image_bytes)
            logger.debug("Image successfully encoded to base64")
            
            # Format instructions for the output parser
            # format_instructions = self.output_parser.get_format_instructions()
            format_instructions = "Give response in plain text output without any formatting, don't use markdown"
            logger.info(f"Format instructions: {format_instructions}")
            
            # Create the messages for the OpenAI API
            messages = [
                {
                    "role": "system",
                    "content": f"{self.system_prompt}\n\n{format_instructions}"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this food image and provide nutritional information."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            logger.info("Sending request to OpenAI vision model")
            logger.debug(f"Request messages structure: {json.dumps(messages, indent=2)}")
            
            logger.info("Sending image to vision model")
            
            # Call the OpenAI API directly
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract the response content
            response_content = response.choices[0].message.content
            logger.info(f"Raw vision model response: {response_content}")

            
            # Parse the response content using food analyzer
            cleaned_result = await self.food_analyzer.analyze_food(response_content)
                        
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