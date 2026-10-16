from dataclasses import dataclass


@dataclass(frozen=True)
class ObservabilityConfig:
    app_name: str = "fastapi-app"
    database_url: str = "sqlite:///./observability.db"
    dashboard_path: str = "/admin/observability"
    max_payload_chars: int = 12_000
    default_page_size: int = 50

    def __post_init__(self) -> None:
        if not self.dashboard_path.startswith("/"):
            raise ValueError("dashboard_path must start with '/'")
        if self.max_payload_chars < 256:
            raise ValueError("max_payload_chars must be at least 256")
        if not 1 <= self.default_page_size <= 200:
            raise ValueError("default_page_size must be between 1 and 200")
