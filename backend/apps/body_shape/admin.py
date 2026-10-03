from django.contrib import admin

from .models import BodyMeasurement, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "display_name", "user", "currency_code", "updated_at")
    search_fields = ("display_name", "user__username", "user__email")


@admin.register(BodyMeasurement)
class BodyMeasurementAdmin(admin.ModelAdmin):
    list_display = ("profile", "measured_on", "styling_shape", "updated_at")
    list_filter = ("styling_shape",)
    date_hierarchy = "measured_on"
