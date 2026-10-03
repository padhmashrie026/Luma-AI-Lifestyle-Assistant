from datetime import date
import re

from django.db.models import Q
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Expense
from .serializers import ExpenseSerializer, ExpenseSummaryQuerySerializer
from .summaries import build_expense_summary


def _positive_query_integer(params, key):
    value = params.get(key)
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValidationError({key: "Enter a valid integer."})
    if parsed < 1:
        raise ValidationError({key: "Enter a positive integer."})
    return parsed


def _query_date(params, key):
    value = params.get(key)
    if value in (None, ""):
        return None
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError({key: "Enter a valid date in YYYY-MM-DD format."})
    if parsed.isoformat() != value:
        raise ValidationError({key: "Enter a valid date in YYYY-MM-DD format."})
    return parsed


class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        expenses = Expense.objects.select_related("profile", "category", "daily_plan").all()
        params = self.request.query_params
        profile_id = _positive_query_integer(params, "profile_id")
        category_id = _positive_query_integer(params, "category_id")
        daily_plan_id = _positive_query_integer(params, "daily_plan_id")
        start_date = _query_date(params, "start_date")
        end_date = _query_date(params, "end_date")
        month = params.get("month", "")

        if month:
            if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
                raise ValidationError({"month": "Enter a month in YYYY-MM format."})
            year, month_number = (int(part) for part in month.split("-"))
            month_start = date(year, month_number, 1)
            next_month = date(year + (month_number == 12), 1 if month_number == 12 else month_number + 1, 1)
            expenses = expenses.filter(spent_on__gte=month_start, spent_on__lt=next_month)
        if start_date:
            expenses = expenses.filter(spent_on__gte=start_date)
        if end_date:
            expenses = expenses.filter(spent_on__lte=end_date)
        if start_date and end_date and start_date > end_date:
            raise ValidationError({"date_range": "start_date must be on or before end_date."})
        if profile_id:
            expenses = expenses.filter(profile_id=profile_id)
        if category_id:
            expenses = expenses.filter(category_id=category_id)
        category_name = params.get("category", "").strip()
        if category_name:
            expenses = expenses.filter(category__name__iexact=category_name)
        if daily_plan_id:
            expenses = expenses.filter(daily_plan_id=daily_plan_id)
        search = params.get("q", "").strip()
        if search:
            expenses = expenses.filter(Q(description__icontains=search) | Q(notes__icontains=search))
        return expenses


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.select_related("profile", "category", "daily_plan").all()
    serializer_class = ExpenseSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class ExpenseSummaryView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        serializer = ExpenseSummaryQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        month_text = values.get("month") or timezone.localdate().strftime("%Y-%m")
        month = date.fromisoformat(f"{month_text}-01")
        return Response(build_expense_summary(values["profile_id"], month))
