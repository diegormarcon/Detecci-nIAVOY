from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    POSTGRES_USER: str = "voi_user"
    POSTGRES_PASSWORD: str = "voi_password"
    POSTGRES_DB: str = "voi_detection"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8005
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Storage
    STORAGE_TYPE: str = "local"
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    EVIDENCE_DIR: str = "./evidence"
    
    # Detection
    DETECTION_MODEL: str = "yolov8n.pt"
    DETECTION_CONFIDENCE: float = 0.25
    DETECTION_IOU_THRESHOLD: float = 0.45
    TRACKING_MIN_HITS: int = 3
    TRACKING_MAX_AGE: int = 30
    
    # Speed
    SPEED_FPS: int = 10
    SPEED_MIN_DISTANCE: float = 2.0
    SPEED_FILTER_WINDOW: int = 5
    
    # Camera
    CAMERA_RTSP_TIMEOUT: int = 5
    CAMERA_MAX_RETRIES: int = 3
    
    # Development
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    @property
    def DATABASE_URL(self) -> str:
        # Usar SQLite para desarrollo local si PostgreSQL no está disponible
        if self.POSTGRES_HOST == "postgres" and not os.getenv("USE_POSTGRES"):
            return "sqlite:///./voi_detection.db"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

