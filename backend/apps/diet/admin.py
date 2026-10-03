from django.contrib import admin

from .models import FoodPreference, GroceryItem, Ingredient, Meal, MealIngredient, MealPlan, MealPlanItem


@admin.register(FoodPreference)
class FoodPreferenceAdmin(admin.ModelAdmin):
    list_display = ("profile", "preference_type", "name", "updated_at")
    list_filter = ("preference_type",)
    search_fields = ("name", "profile__display_name")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)


class MealIngredientInline(admin.TabularInline):
    model = MealIngredient
    extra = 0


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("name", "profile", "meal_type", "updated_at")
    list_filter = ("meal_type",)
    search_fields = ("name", "profile__display_name")
    inlines = (MealIngredientInline,)


@admin.register(MealIngredient)
class MealIngredientAdmin(admin.ModelAdmin):
    list_display = ("meal", "ingredient", "quantity", "unit")
    search_fields = ("meal__name", "ingredient__name")


class MealPlanItemInline(admin.TabularInline):
    model = MealPlanItem
    extra = 0


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ("profile", "plan_date", "updated_at")
    date_hierarchy = "plan_date"
    inlines = (MealPlanItemInline,)


@admin.register(MealPlanItem)
class MealPlanItemAdmin(admin.ModelAdmin):
    list_display = ("meal_plan", "slot", "meal", "scheduled_time", "is_completed")
    list_filter = ("slot", "is_completed")


@admin.register(GroceryItem)
class GroceryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "profile", "meal_plan", "quantity", "unit", "is_purchased")
    list_filter = ("is_purchased",)
    search_fields = ("name", "profile__display_name")
