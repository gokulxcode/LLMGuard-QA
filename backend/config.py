import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environmental variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

class Settings(BaseSettings):
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    JWT_SECRET: str = "super_secret_llm_guard_qa_jwt_token_key_change_me_in_production_12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    DATABASE_URL: str = "sqlite:///./llmguard_qa.db"
    
    GEMINI_API_KEY: str = ""
    
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@llmguard.qa"
    ADMIN_PASSWORD: str = "adminpassword"
    
    class Config:
        case_sensitive = True

settings = Settings()
