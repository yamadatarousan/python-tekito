from datetime import date, timedelta

from app.domain.dashboard import build_dashboard_metrics
from app.domain.entities import TaskSnapshot, TaskStatus


def test_期限切れと進捗率を集計できる() -> None:
    # 意図: 期限切れ判定は「完了以外」かつ「期限日が今日より前」を数える仕様を担保する。
    today = date(2026, 3, 19)
    snapshots = [
        TaskSnapshot(id=1, title="要件定義", status=TaskStatus.todo, due_date=today - timedelta(days=1)),
        TaskSnapshot(id=2, title="実装", status=TaskStatus.in_progress, due_date=today + timedelta(days=1)),
        TaskSnapshot(id=3, title="テスト", status=TaskStatus.done, due_date=today - timedelta(days=2)),
    ]

    metrics = build_dashboard_metrics(snapshots=snapshots, today=today)

    assert metrics.total_count == 3
    assert metrics.done_count == 1
    assert metrics.overdue_count == 1
    assert metrics.completion_rate == 33


def test_タスクが0件のとき進捗率は0になる() -> None:
    # 前提: ゼロ除算を避けるため、0件時は固定で0%を返す。
    metrics = build_dashboard_metrics(snapshots=[], today=date(2026, 3, 19))

    assert metrics.total_count == 0
    assert metrics.completion_rate == 0
