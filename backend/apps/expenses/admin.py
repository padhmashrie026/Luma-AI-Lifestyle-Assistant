from django.contrib import admin

from .models import BudgetCategory, Expense, Income


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ("source", "profile", "amount", "received_on")
    date_hierarchy = "received_on"
    search_fields = ("source", "profile__display_name")


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "profile", "monthly_limit", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "profile__display_name")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("description", "profile", "category", "amount", "spent_on", "daily_plan")
    list_filter = ("category",)
    date_hierarchy = "spent_on"
    search_fields = ("description", "profile__display_name")
