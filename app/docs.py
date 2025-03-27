from fastapi.openapi.utils import get_openapi

def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="CaloriesTracker API",
        version="1.0.0",
        description="""
        CaloriesTracker API helps you track and analyze your food intake.
        
        Features:
        - Analyze food descriptions for nutritional information
        - Upload food images for automatic nutritional analysis
        - Track and retrieve food consumption logs
        """,
        routes=app.routes,
    )

    # Custom tags metadata
    openapi_schema["tags"] = [
        {
            "name": "Food Analysis",
            "description": "Endpoints for analyzing food through text descriptions and images",
        },
        {
            "name": "Food Logs",
            "description": "Endpoints for managing food consumption logs",
        },
    ]

    # Add security scheme for future authentication
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }

    # Enhance endpoint documentation
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if operation["summary"] == "Analyze Food":
                operation.update(
                    {
                        "tags": ["Food Analysis"],
                        "description": """
                        Analyze a food description to get nutritional information.
                        Returns detailed breakdown of calories, macronutrients, and micronutrients.
                        """,
                    }
                )
            elif operation["summary"] == "Track Food Image":
                operation.update(
                    {
                        "tags": ["Food Analysis"],
                        "description": """
                        Upload a food image for automatic nutritional analysis.
                        The AI model will analyze the image and provide detailed nutritional information.
                        """,
                    }
                )
            elif "logs" in operation["summary"].lower():
                operation.update(
                    {
                        "tags": ["Food Logs"],
                        "description": "Retrieve food consumption logs with detailed nutritional information.",
                    }
                )

    app.openapi_schema = openapi_schema
    return app.openapi_schema