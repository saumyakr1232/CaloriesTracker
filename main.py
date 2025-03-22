from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
import langchain
from app.database import engine
from app.models import database_models

# Create database tables
database_models.Base.metadata.create_all(bind=engine)

# Enable LangChain debug mode
langchain.debug = True

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Food Nutrition Analyzer API"}
