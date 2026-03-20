# 学習タスク管理アプリ (FastAPI + SQLite)

Python学習用として、現場でよく使われる構成を意識したWebアプリです。

- Webフレームワーク: FastAPI
- ORM: SQLAlchemy
- DB: SQLite
- テンプレート: Jinja2
- テスト: pytest

## 何を学べるか

- ルーター / サービス / リポジトリの責務分離
- APIとサーバーサイド描画を同じバックエンドで共存させる設計
- SQLiteを使ったローカル開発
- ドメインロジックの単体テストとAPI統合テスト

## 機能

- プロジェクト作成
- タスク作成（タイトル / 説明 / 期限日）
- タスク状態更新（todo -> in_progress -> done）
- 状態で絞り込み
- ダッシュボード集計（総数 / 完了数 / 期限切れ / 進捗率）

## セットアップ

```bash
python3 -m pip install -e '.[dev]'
```

## 起動

```bash
python3 -m uvicorn app.main:app --reload
```

- 画面: `http://127.0.0.1:8000`
- APIドキュメント: `http://127.0.0.1:8000/docs`

## テスト

```bash
python3 -m pytest
```

## ディレクトリ構成

```text
app/
  core/            # 設定
  domain/          # 純粋ロジック（集計など）
  infrastructure/  # DBモデル・接続
  repositories/    # 永続化アクセス
  services/        # ユースケース
  routers/         # API / Webのエンドポイント
  schemas/         # API入出力スキーマ
  templates/       # Jinja2テンプレート
  static/          # CSS
tests/
```

## 補足

- 学習しやすさを優先して、起動時に `Base.metadata.create_all()` でテーブルを自動作成しています。
- 本番運用では Alembic などのマイグレーションツール導入を推奨します。

## コード読解ガイド

- [docs/コードリーディングガイド.md](docs/コードリーディングガイド.md)
