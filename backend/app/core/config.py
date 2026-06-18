from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DH MDM"
    database_url: str = "postgresql+psycopg://dh_mdm:dh_mdm@localhost:5432/dh_mdm"
    redis_url: str = "redis://localhost:6379/0"
    jwt_issuer: str = "https://login.microsoftonline.com/common/v2.0"
    jwt_audience: str = "api://dh-mdm"
    jwt_jwks_url: AnyHttpUrl = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
    session_secret: str = Field(default="change-me", min_length=8)
    filevault_kek: str = Field(default="change-me-32-byte-minimum-secret", min_length=8)
    cors_origins: list[str] = ["http://localhost:5173"]
    public_base_url: str = "http://localhost:8000"
    mdm_organization: str = "DH Website Services"
    mdm_topic: str = "com.apple.mgmt.External.REPLACE_ME"
    mdm_server_url: str = "http://localhost:8000/api/v1/mdm/connect"
    mdm_checkin_url: str = "http://localhost:8000/api/v1/mdm/checkin"
    mdm_scep_url: str = "http://localhost:8000/scep"
    mdm_scep_challenge: str = "replace-me"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
