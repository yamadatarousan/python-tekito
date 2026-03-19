from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_プロジェクトとタスクを作成して状態更新できる(tmp_path: Path) -> None:
    # 意図: 学習用でも実務で重要な「作成→更新→参照」の一連の流れをAPIレベルで担保する。
    db_file = tmp_path / "app.db"
    app = create_app(database_url=f"sqlite+pysqlite:///{db_file}")

    with TestClient(app) as client:
        project_response = client.post("/api/projects", json={"name": "FastAPI学習"})
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]

        task_response = client.post(
            f"/api/projects/{project_id}/tasks",
            json={
                "title": "初期セットアップ",
                "description": "依存関係を整える",
                "due_date": "2026-03-25",
            },
        )
        assert task_response.status_code == 201
        task_id = task_response.json()["id"]

        update_response = client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "done"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "done"

        dashboard_response = client.get("/api/dashboard")
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        assert dashboard["total_count"] == 1
        assert dashboard["done_count"] == 1
        assert dashboard["completion_rate"] == 100


def test_Web画面でプロジェクト一覧が表示される(tmp_path: Path) -> None:
    # 意図: APIだけでなく、サーバーサイド描画ページが最低限機能することを保証する。
    db_file = tmp_path / "app.db"
    app = create_app(database_url=f"sqlite+pysqlite:///{db_file}")

    with TestClient(app) as client:
        create_response = client.post("/api/projects", json={"name": "画面確認"})
        assert create_response.status_code == 201

        top_response = client.get("/")
        assert top_response.status_code == 200
        assert "画面確認" in top_response.text
        assert "学習タスク管理" in top_response.text


def test_状態でタスクを絞り込みできる(tmp_path: Path) -> None:
    # 意図: UIでよく使う絞り込み条件がAPIでも保証されるようにする。
    db_file = tmp_path / "app.db"
    app = create_app(database_url=f"sqlite+pysqlite:///{db_file}")

    with TestClient(app) as client:
        project_id = client.post("/api/projects", json={"name": "絞り込み検証"}).json()["id"]

        task_1_id = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "未完了タスク", "description": "", "due_date": None},
        ).json()["id"]
        task_2_id = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "完了タスク", "description": "", "due_date": None},
        ).json()["id"]

        client.patch(f"/api/tasks/{task_2_id}/status", json={"status": "done"})

        filtered = client.get(f"/api/projects/{project_id}/tasks?status=done")
        assert filtered.status_code == 200
        payload = filtered.json()
        assert len(payload) == 1
        assert payload[0]["id"] == task_2_id

        # 補足: 念のため未完了側IDが混ざっていないことも明示的に確認する。
        assert payload[0]["id"] != task_1_id
