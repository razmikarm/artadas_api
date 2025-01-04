from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Artadas API"
    debug: bool = False

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str

    secret_key: str
    access_token_timeout: int
    refresh_token_secret: str
    refresh_token_timeout: int
    algorithm: str = "HS256"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# print(24 * "* ", settings.model_dump())
