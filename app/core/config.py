from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Toss Trading Dashboard"
    API_V1_STR: str = "/api/v1"
    
    # KIS Config Path
    KIS_CONFIG_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "kis_devlp.yaml")
    
    class Config:
        case_sensitive = True

settings = Settings()
