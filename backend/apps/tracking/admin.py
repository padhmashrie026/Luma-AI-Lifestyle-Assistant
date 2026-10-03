from django.contrib import admin

from .models import DailyTracking


@admin.register(DailyTracking)
class DailyTrackingAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "track_date",
        "outfit_completed",
        "meals_completed",
        "expenses_reviewed",
        "daily_plan_completed",
    )
    date_hierarchy = "track_date"
