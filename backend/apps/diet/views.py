from datetime import timedelta

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from .planning import _build_grocery_list, _format_meal, _meal_ingredients, generate_weekly_plan
from .serializers import MealSerializer, SaveWeeklyMealPlanSerializer, WeeklyMealPlanRequestSerializer
from apps.body_shape.models import Profile
from .models import Meal, MealPlan, MealPlanItem


class MealListCreateView(generics.ListCreateAPIView):
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]

    def get_profile(self):
        return get_object_or_404(Profile, user=self.request.user)

    def get_queryset(self):
        return Meal.objects.filter(profile=self.get_profile()).prefetch_related("meal_ingredients__ingredient")

    def perform_create(self, serializer):
        serializer.save()


class MealDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return Meal.objects.filter(profile=profile).prefetch_related("meal_ingredients__ingredient")


class WeeklyMealPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WeeklyMealPlanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = get_object_or_404(Profile, user=request.user)
        result = generate_weekly_plan(profile_id=profile.id, **serializer.validated_data)
        return Response(result)


class SavedWeeklyMealPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        plans = list(MealPlan.objects.filter(profile=profile).prefetch_related(
            "items__meal__meal_ingredients__ingredient"
        ).order_by("-plan_date"))
        by_date = {plan.plan_date: plan for plan in plans}
        for latest_date in sorted(by_date, reverse=True):
            start = latest_date - timedelta(days=6)
            week = [by_date.get(start + timedelta(days=index)) for index in range(7)]
            if any(plan is None for plan in week):
                continue
            if any(not {item.slot for item in plan.items.all()} >= {"breakfast", "lunch", "dinner"} for plan in week):
                continue
            return Response(self._serialize_week(start, week))
        return Response({"plan_available": False, "saved": False})

    def post(self, request):
        serializer = SaveWeeklyMealPlanSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        profile = get_object_or_404(Profile, user=request.user)
        start = serializer.validated_data["week_start"]
        days = serializer.validated_data["weekly_plan"]
        with transaction.atomic():
            created_plans = []
            for day in days:
                meal_plan = MealPlan.objects.create(profile=profile, plan_date=day["date"])
                created_plans.append(meal_plan)
                for slot in ("breakfast", "lunch", "dinner", "snack"):
                    meal_id = day["meals"].get(slot)
                    if meal_id is not None:
                        MealPlanItem.objects.create(meal_plan=meal_plan, meal=serializer._owned_meals[meal_id], slot=slot)
        return Response(self._serialize_week(start, created_plans), status=201)

    @staticmethod
    def _serialize_week(start, plans):
        weekly_plan = []
        grocery_meals = []
        for plan in plans:
            slots = {item.slot: item.meal for item in plan.items.all()}
            formatted = {}
            for slot in ("breakfast", "lunch", "dinner", "snack"):
                meal = slots.get(slot)
                if meal:
                    links = _meal_ingredients(meal)
                    formatted[slot] = _format_meal(meal, links)
                    grocery_meals.append(meal)
                else:
                    formatted[slot] = None
            weekly_plan.append({"date": plan.plan_date.isoformat(), "meals": formatted})
        end = start + timedelta(days=6)
        return {
            "plan_available": True, "saved": True,
            "week_start": start.isoformat(), "week_end": end.isoformat(),
            "weekly_plan": weekly_plan, "grocery_list": _build_grocery_list(grocery_meals),
            "budget": {"available": False, "estimated_daily": None, "estimated_weekly": None,
                       "reason": "Meal and ingredient models do not store prices or budget amounts."},
            "nutrition_note": "Ingredient-name tags are broad planning hints, not nutrition analysis or medical advice.",
            "preparation_note": "Preparation guidance uses saved preparation times and descriptions; no cooking steps are invented.",
        }
