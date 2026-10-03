from datetime import timedelta

from django.db.models import Count, Q

from .models import DailyTracking

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
    for record in records.order_by("track_date"):
        day_completed = sum(bool(getattr(record, field)) for field in COMPLETION_FIELDS)
        daily_rows.append({
            "date": record.track_date.isoformat(),
            "completed_tasks": day_completed,
            "pending_tasks": len(COMPLETION_FIELDS) - day_completed,
            "completion_percentage": round(day_completed * 100 / len(COMPLETION_FIELDS), 2),
        })
    return {
        "profile_id": profile_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "tracking_days": aggregate["tracking_days"],
        "completed_tasks": completed,
        "pending_tasks": total_slots - completed,
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
