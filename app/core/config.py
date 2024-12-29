from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    debug: bool = False

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# print(24 * "* ", settings.model_dump())
