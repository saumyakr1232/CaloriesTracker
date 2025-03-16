import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class FoodAnalyzerService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
        )
        
        self.response_schemas = [
            ResponseSchema(name="description", description="A cleaned up description of the food"),
            ResponseSchema(name="calories", description="Estimated total calories as a number"),
            ResponseSchema(name="macronutrients", description="Macronutrients breakdown in grams"),
            ResponseSchema(name="micronutrients", description="Key micronutrients and their amounts"),
        ]
        
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        
        self.prompt_template = ChatPromptTemplate.from_template("""
            You are a nutritionist expert that analyzes food descriptions and provides detailed nutritional information.

            Analyze the following food description and provide:
            1. A cleaned up description
            2. Estimated total calories
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
            
            result = self.output_parser.parse(response.content)
            logger.info("Successfully parsed LLM response")
            logger.debug(f"Parsed result: {result}")
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing food description: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error analyzing food description: {str(e)}") 