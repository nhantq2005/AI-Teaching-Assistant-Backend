from pathlib import Path

import cloudinary
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "AI Teaching Assistant"

    DATABASE_URL: str
    ALEMBIC_DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    UPLOAD_DIR: Path = Path("storage/uploads")
    EXTRACTED_DIR: Path = Path("storage/extracted")
    PROCESSED_DIR: Path = Path("storage/processed")

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "document_chunks"

    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_BATCH_SIZE: int = 16

    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def configure_cloudinary(self):
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True
        )


settings = Settings()