from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 뉴스 DB
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # 수어 DB
    SIGN_DB_HOST: str
    SIGN_DB_PORT: int
    SIGN_DB_USER: str
    SIGN_DB_PASSWORD: str
    SIGN_DB_NAME: str

    ANTHROPIC_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
