import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", None)
    OPENAI_APIKEY: Optional[str] = os.getenv("OPENAI_APIKEY", None)


settings = Settings()
