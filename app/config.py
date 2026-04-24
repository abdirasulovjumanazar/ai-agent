from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    class Config:
        env_file = ".env"


settings = Settings()
