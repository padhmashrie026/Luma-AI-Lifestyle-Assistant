from datetime import timedelta
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.body_shape.models import BodyMeasurement, Profile
from apps.diet.models import Meal, MealPlan
from apps.expenses.models import BudgetCategory, Expense
from apps.lifestyle.models import DailyPlan
from apps.outfits.models import Outfit
from apps.tracking.models import DailyTracking
from apps.wardrobe.models import WardrobeItem
from .serializers import InsightsQuerySerializer


class InsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = InsightsQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        values = query.validated_data
        end_date = values.get("end_date") or timezone.localdate()
        start_date = values.get("start_date") or end_date - timedelta(days=6)
        if start_date > end_date:
            raise ValidationError({"date_range": "start_date must be on or before end_date."})

        profile = get_object_or_404(Profile, user=request.user)
        expenses = Expense.objects.filter(
            profile=profile, category__profile=profile, spent_on__range=(start_date, end_date)
        )
        tracking = DailyTracking.objects.filter(profile=profile, track_date__range=(start_date, end_date))
        by_category = expenses.values("category_id", "category__name").annotate(total=Sum("amount")).order_by("category__name", "category_id")
        daily_progress = []
        for row in tracking.order_by("track_date"):
            completed = sum((row.outfit_completed, row.meals_completed, row.expenses_reviewed, row.daily_plan_completed))
            daily_progress.append({"date": row.track_date.isoformat(), "completed_tasks": completed,
                                   "pending_tasks": 4 - completed, "completion_percentage": round(completed * 25, 2)})

        total_expenses = expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        tracking_days = tracking.count()
        completed_tasks = sum(row["completed_tasks"] for row in daily_progress)
        return Response({
            "profile_id": profile.id,
            "currency_code": profile.currency_code,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "overview": {
                "wardrobe_items": WardrobeItem.objects.filter(profile=profile).count(),
                "outfits": Outfit.objects.filter(profile=profile).count(),
                "meals": Meal.objects.filter(profile=profile).count(),
                "meal_plans": MealPlan.objects.filter(profile=profile).count(),
                "daily_plans": DailyPlan.objects.filter(profile=profile).count(),
                "measurements": BodyMeasurement.objects.filter(profile=profile).count(),
                "budget_categories": BudgetCategory.objects.filter(profile=profile).count(),
            },
            "period": {
                "expense_total": format(total_expenses, ".2f"), "expense_count": expenses.count(),
                "tracking_days": tracking_days, "completed_tasks": completed_tasks,
                "pending_tasks": tracking_days * 4 - completed_tasks,
                "completion_percentage": round(completed_tasks * 100 / (tracking_days * 4), 2) if tracking_days else 0.0,
            },
            "spending_by_category": [
                {"category_id": row["category_id"], "category": row["category__name"],
                 "spent": format(row["total"] or Decimal("0.00"), ".2f")} for row in by_category
            ],
            "daily_progress": daily_progress,
        })
