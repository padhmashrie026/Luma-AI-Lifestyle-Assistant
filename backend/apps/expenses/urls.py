from django.urls import path

from .views import ExpenseDetailView, ExpenseListCreateView, ExpenseSummaryView


urlpatterns = [
    path("summary/", ExpenseSummaryView.as_view(), name="expense-summary"),
    path("", ExpenseListCreateView.as_view(), name="expense-list-create"),
    path("<int:pk>/", ExpenseDetailView.as_view(), name="expense-detail"),
]
