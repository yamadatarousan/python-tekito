from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_engine_from_url(database_url: str) -> Engine:
    """DBエンジンを生成する。

    制約:
    - SQLiteはスレッド境界をまたぐ接続制約があるため、check_same_thread=False を指定する。
    """

    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(database_url, connect_args=connect_args)


def create_session_factory(engine: Engine) -> sessionmaker:
    """セッションファクトリーを生成する。"""

    return sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False, class_=Session)
