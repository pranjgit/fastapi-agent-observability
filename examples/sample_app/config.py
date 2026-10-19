import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Search for .env in current working dir, sample_app dir, or parent dirs
current_dir = Path(__file__).resolve().parent
for env_path in [
    current_dir / ".env",
    current_dir.parent / ".env",
    current_dir.parent.parent / ".env",
]:
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path)
        break


@dataclass(frozen=True)
class Settings:
    # Application & Server
    app_name: str = os.getenv("APP_NAME", "FastAPI Agent Observability Demo")
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

    # Observability Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./observability.db")
    dashboard_path: str = os.getenv("DASHBOARD_PATH", "/admin/observability")
    max_payload_chars: int = int(os.getenv("MAX_PAYLOAD_CHARS", "12000"))
    default_page_size: int = int(os.getenv("DEFAULT_PAGE_SIZE", "50"))

    # Authentication & Authorization Tokens
    admin_api_key: str = os.getenv("ADMIN_API_KEY", "admin-secret-key-123")
    user_api_key: str = os.getenv("USER_API_KEY", "user-secret-key-456")
    dev_mode_auto_admin: bool = os.getenv("DEV_MODE_AUTO_ADMIN", "false").lower() in ("true", "1", "yes")

    # Optional LLM API Keys
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")


settings = Settings()
