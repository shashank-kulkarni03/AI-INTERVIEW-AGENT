from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    GEMINI_API_KEY: str

    DATABASE_URL: str

    ALIGNMENT_THRESHOLD: float = 60.0

    MIN_INTERVIEW_QUESTIONS: int = 5

    MAX_INTERVIEW_QUESTIONS: int = 10

    MAX_FOLLOWUPS_PER_QUESTION: int = 1

    UPLOAD_DIR: str = "uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()