from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """環境変数から読み込む設定値。"""

    app_name: str = "学習タスク管理"
    # 共有しやすさを優先し、SQLiteファイルをプロジェクト直下に置く。
    database_url: str = "sqlite+pysqlite:///./learning_tasks.db"

    model_config = SettingsConfigDict(env_prefix="LEARNING_APP_")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """設定を使い回して、毎リクエストの読み込みコストを避ける。"""

    return Settings()
