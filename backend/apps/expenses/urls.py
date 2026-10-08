from django.urls import path

from .views import BudgetCategoryListCreateView, ExpenseDetailView, ExpenseListCreateView, ExpenseSummaryView


urlpatterns = [
    path("summary/", ExpenseSummaryView.as_view(), name="expense-summary"),
    path("categories/", BudgetCategoryListCreateView.as_view(), name="budget-category-list-create"),
    path("", ExpenseListCreateView.as_view(), name="expense-list-create"),
    path("<int:pk>/", ExpenseDetailView.as_view(), name="expense-detail"),
]
