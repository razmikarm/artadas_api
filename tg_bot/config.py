from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AUTH_BASE_URL: str

    TG_BOT_TOKEN: str
    TG_FREE_GROUP_ID: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
