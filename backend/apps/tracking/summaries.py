from datetime import timedelta
from collections import defaultdict

from django.db.models import Count, Q

from .models import DailyTracking
from apps.lifestyle.models import DailyTask

COMPLETION_FIELDS = (
    "outfit_completed",
    "meals_completed",
    "expenses_reviewed",
    "daily_plan_completed",
)


def build_tracking_summary(profile_id, start_date, end_date):
    records = DailyTracking.objects.filter(
        profile_id=profile_id, track_date__range=(start_date, end_date)
    )
    aggregate = records.aggregate(
        tracking_days=Count("id"),
        **{
            f"{field}_count": Count("id", filter=Q(**{field: True}))
            for field in COMPLETION_FIELDS
        },
    )
    total_slots = aggregate["tracking_days"] * len(COMPLETION_FIELDS)
    completed = sum(aggregate[f"{field}_count"] for field in COMPLETION_FIELDS)
    daily_rows = []
    progress_by_date = {}
    for record in records.order_by("track_date"):
        day_completed = sum(bool(getattr(record, field)) for field in COMPLETION_FIELDS)
        progress_by_date[record.track_date] = {
            "date": record.track_date.isoformat(),
            "completed_tasks": day_completed,
            "pending_tasks": len(COMPLETION_FIELDS) - day_completed,
            "_total": len(COMPLETION_FIELDS),
        }
    task_counts = defaultdict(lambda: {"completed": 0, "pending": 0})
    for task in DailyTask.objects.filter(profile_id=profile_id, task_date__range=(start_date, end_date)).values_list("task_date", "is_completed"):
        key = "completed" if task[1] else "pending"
        task_counts[task[0]][key] += 1
    task_total = sum(counts["completed"] + counts["pending"] for counts in task_counts.values())
    for task_date, counts in task_counts.items():
        row = progress_by_date.setdefault(task_date, {
            "date": task_date.isoformat(), "completed_tasks": 0, "pending_tasks": 0, "_total": 0,
        })
        row["completed_tasks"] += counts["completed"]
        row["pending_tasks"] += counts["pending"]
        row["_total"] += counts["completed"] + counts["pending"]
    for row in progress_by_date.values():
        total = row.pop("_total")
        row["completion_percentage"] = round(row["completed_tasks"] * 100 / total, 2) if total else 0.0
        daily_rows.append(row)
    daily_rows.sort(key=lambda row: row["date"])
    completed += sum(counts["completed"] for counts in task_counts.values())
    pending_tasks = aggregate["tracking_days"] * len(COMPLETION_FIELDS) - sum(
        aggregate[f"{field}_count"] for field in COMPLETION_FIELDS
    ) + sum(counts["pending"] for counts in task_counts.values())
    total_slots = aggregate["tracking_days"] * len(COMPLETION_FIELDS) + task_total
    return {
        "profile_id": profile_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "tracking_days": aggregate["tracking_days"],
        "completed_tasks": completed,
        "pending_tasks": pending_tasks,
        "completion_percentage": round(completed * 100 / total_slots, 2) if total_slots else 0.0,
        "progress_by_field": {
            field: {
                "completed_days": aggregate[f"{field}_count"],
                "tracking_days": aggregate["tracking_days"],
                "completion_percentage": round(
                    aggregate[f"{field}_count"] * 100 / aggregate["tracking_days"], 2
                ) if aggregate["tracking_days"] else 0.0,
            }
            for field in COMPLETION_FIELDS
        },
        "daily_progress": daily_rows,
    }
