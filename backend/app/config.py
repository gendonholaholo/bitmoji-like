from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # YouCam API Configuration
    youcam_api_key: str
    youcam_secret_key: str | None = None  # Not used in v2 API
    youcam_base_url: str = "https://yce-api-01.makeupar.com/s2s/v2.0"

    # OpenAI API Configuration (for AI-powered skin analysis)
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    ai_analysis_enabled: bool = True  # Toggle to enable/disable AI analysis

    # Development settings
    bypass_youcam: bool = False  # Bypass YouCam API for development (uses mock data)

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
