from django.contrib import admin

from .models import WardrobeItem


@admin.register(WardrobeItem)
class WardrobeItemAdmin(admin.ModelAdmin):
    list_display = ("name", "profile", "category", "color", "status", "updated_at")
    list_filter = ("category", "status")
    search_fields = ("name", "color", "brand", "profile__display_name")
