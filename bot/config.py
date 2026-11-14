from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Имена переменных в классе автоматически сопоставляются с именами в .env (без учета регистра)
    bot_token: SecretStr
    db_url: SecretStr

    # Указываем, откуда читать переменные, если запускаем локально без Docker
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Игнорировать лишние переменные из .env (например, POSTGRES_USER)
    )


config = Settings()