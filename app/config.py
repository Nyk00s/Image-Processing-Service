from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Config(BaseSettings):

    # Database
    database_url: str
    redis_url: str

    # MinIO
    s3_endpoint_url: str
    s3_access_key: str
    s3_secret_key: SecretStr
    s3_bucket: str
    s3_region: str = 'us-east-1'

    # JWT
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7

    # Rate limit
    upload_rate_limit: int = 10
    rate_limit_window_seconds: int = 3600

    # Upload settings
    max_upload_size_mb: int
    presigned_url_ttl_seconds: int = 900

    app_env: str = 'dev'
    log_level: str = 'DEBUG'

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )