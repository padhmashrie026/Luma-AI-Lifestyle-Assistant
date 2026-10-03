from django.contrib import admin

from .models import Outfit, OutfitItem


class OutfitItemInline(admin.TabularInline):
    model = OutfitItem
    extra = 0


@admin.register(Outfit)
class OutfitAdmin(admin.ModelAdmin):
    list_display = ("name", "profile", "occasion", "updated_at")
    list_filter = ("occasion",)
    search_fields = ("name", "profile__display_name")
    inlines = (OutfitItemInline,)


@admin.register(OutfitItem)
class OutfitItemAdmin(admin.ModelAdmin):
    list_display = ("outfit", "item", "slot", "position")
    list_filter = ("slot",)
    search_fields = ("outfit__name", "item__name")
