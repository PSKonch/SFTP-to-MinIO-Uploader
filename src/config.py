from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_NAME: str = "pg"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "1234"

    @property
    def POSTGRES_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME}"

    SMTP_SERVER: str = "smtp.example.com"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    @property
    def RABBITMQ_URL(self):
        return f"pyamqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()