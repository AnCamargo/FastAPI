from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    db_user: str 
    db_pw: str 
    db_host: str
    db_port: int
    db_name: str 
    secret_key: str 
    algorithm: str 
    token_mins_expire: int 

    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")

settings = Settings()