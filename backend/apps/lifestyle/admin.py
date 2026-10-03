from django.contrib import admin

from .models import DailyPlan


@admin.register(DailyPlan)
class DailyPlanAdmin(admin.ModelAdmin):
    list_display = ("profile", "plan_date", "outfit", "meal_plan", "updated_at")
    date_hierarchy = "plan_date"
