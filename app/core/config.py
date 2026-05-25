"""应用配置管理模块。"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """从环境变量或 .env 文件读取项目配置。"""

    app_name: str = "Smart Data Agent"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    streamlit_port: int = 8501
    api_base_url: str = "http://localhost:8000"

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "smart_data_agent"
    mysql_user: str = "smart_agent"
    mysql_password: str = "smart_agent_password"
    mysql_root_password: str = "root_password"

    llm_provider: str = "openai-compatible"
    llm_api_key: str = Field(default="", repr=False)
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0

    sql_default_limit: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """拼接 SQLAlchemy 使用的 MySQL 连接地址。"""
        return (
            "mysql+pymysql://"
            f"{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            "?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    """缓存配置对象，避免重复解析环境变量。"""
    return Settings()


settings = get_settings()
