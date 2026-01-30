"""Configuration management using pydantic-settings"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Server
    environment: str = Field(default="development", alias="ENVIRONMENT")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # Database
    database_url: str = Field(
        default="postgresql://localhost:5432/cloudbot_platform",
        alias="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    # JWT
    jwt_secret_key: str = Field(default="dev-secret-change-in-production", alias="JWT_SECRET_KEY")
    jwt_refresh_secret_key: str = Field(
        default="dev-refresh-secret-change-in-production",
        alias="JWT_REFRESH_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # Encryption
    encryption_key: str = Field(
        default="dev-encryption-key-32-bytes!!",
        alias="ENCRYPTION_KEY"
    )

    # AWS
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    ec2_security_group_id: Optional[str] = Field(default=None, alias="EC2_SECURITY_GROUP_ID")
    ec2_subnet_id: Optional[str] = Field(default=None, alias="EC2_SUBNET_ID")
    ec2_key_pair_name: str = Field(default="cloudbot-key", alias="EC2_KEY_PAIR_NAME")
    ubuntu_ami_id: str = Field(
        default="ami-0c55b159cbfafe1f0",
        alias="UBUNTU_AMI_ID"
    )  # Ubuntu 24.04 LTS in us-east-1

    # Features
    local_dev_mode: bool = Field(default=False, alias="LOCAL_DEV_MODE")
    max_instances_per_user: int = Field(default=2, alias="MAX_INSTANCES_PER_USER")
    control_plane_url: Optional[str] = Field(default=None, alias="CONTROL_PLANE_URL")  # Public URL for instances to access
    moltbot_tarball_url: Optional[str] = Field(default=None, alias="MOLTBOT_TARBALL_URL")  # S3 URL for moltbot tarball

    # CORS
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="CORS_ORIGINS"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins


# Global settings instance
settings = Settings()


def validate_production_config():
    """Validate critical configuration for production environment"""
    if settings.environment == "production":
        required_fields = [
            ("JWT_SECRET_KEY", settings.jwt_secret_key),
            ("JWT_REFRESH_SECRET_KEY", settings.jwt_refresh_secret_key),
            ("ENCRYPTION_KEY", settings.encryption_key),
            ("DATABASE_URL", settings.database_url),
        ]

        for field_name, field_value in required_fields:
            if not field_value or "dev-" in field_value:
                raise ValueError(
                    f"Production environment requires valid {field_name}. "
                    f"Generate secure values and set them in environment variables."
                )

        print("✅ Production configuration validated")
    else:
        print(f"⚠️  Running in {settings.environment} mode")
