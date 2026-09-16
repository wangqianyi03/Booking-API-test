import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not str(value).strip():
        raise RuntimeError(f"请在 .env 中配置 {name}")
    return value


class Settings:
    def __init__(self):
        load_dotenv(ROOT_DIR / ".env", override=False)

        self.env_name = os.getenv("TEST_ENV", "local")
        yaml_path = ROOT_DIR / "config" / "env" / f"{self.env_name}.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"找不到环境配置文件: {yaml_path}")

        with yaml_path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}

        self.base_url = os.getenv("BASE_URL", data["base_url"]).rstrip("/")
        self.timeout = int(os.getenv("TIMEOUT", data.get("timeout", 10)))
        self.log_level = os.getenv("LOG_LEVEL", data.get("log_level", "INFO")).upper()
        self.username = _require_env("AUTH_USERNAME")
        self.password = _require_env("AUTH_PASSWORD")
        self.log_dir = ROOT_DIR / "logs"
        self.data_dir = ROOT_DIR / "data"
        self.report_dir = ROOT_DIR / "reports"


settings = Settings()
