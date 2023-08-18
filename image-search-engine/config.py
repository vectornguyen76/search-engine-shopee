import os
from pydantic_settings import BaseSettings

basedir = os.path.abspath(os.path.dirname(__file__))

class Settings(BaseSettings):
    # App config
    APP_NAME: str = "API Image Search Engine"
    APP_ENV: str = "develop"
    
    # Logging setting
    DATE_FMT: str = '%Y-%m-%d %H:%M:%S'
    LOG_DIR: str = f'{basedir}/logs/api.log'
    
    IMAGEDIR:str = "images/"
    

settings = Settings()