from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # YouCam API Configuration
    youcam_api_key: str
    youcam_secret_key: str | None = None  # Not used in v2 API
    youcam_base_url: str = "https://yce-api-01.makeupar.com/s2s/v2.0"

    # Application settings
    upload_dir: str = "/tmp/uploads"
    results_dir: str = "/tmp/results"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    # CORS settings (will be parsed from comma-separated string)
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
