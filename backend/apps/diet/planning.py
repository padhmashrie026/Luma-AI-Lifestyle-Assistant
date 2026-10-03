"""Rule-based weekly meal planning from meals and preferences already stored."""

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from .models import FoodPreference, Meal, MealIngredient


SLOT_TYPES = ("breakfast", "lunch", "dinner", "snack")
REQUIRED_TYPES = ("breakfast", "lunch", "dinner")

# These transparent name checks are broad hints only, not a nutrient analysis.
INGREDIENT_HINTS = {
    "protein": (
        "lentil", "dal", "bean", "chickpea", "chana", "tofu", "paneer", "egg",
        "chicken", "fish", "salmon", "tuna", "yogurt", "yoghurt", "tempeh", "pea",
    ),
    "healthy_fats": (
        "avocado", "olive oil", "nuts", "almond", "walnut", "cashew", "peanut",
        "chia", "flax", "sesame", "sunflower seed", "pumpkin seed",
    ),
    "fibre_vegetables": (
        "vegetable", "spinach", "broccoli", "carrot", "tomato", "cauliflower", "cabbage",
        "pepper", "courgette", "zucchini", "oat", "whole grain", "brown rice", "fruit",
        "apple", "berry", "beans", "lentil", "chickpea",
    ),
}


def _meal_ingredients(meal):
    return list(
        MealIngredient.objects.filter(meal=meal)
        .select_related("ingredient")
        .order_by("ingredient__name", "id")
    )


def _meal_text(meal, ingredient_links):
    parts = [meal.name, meal.description]
    parts.extend(link.ingredient.name for link in ingredient_links)
    return " ".join(parts).casefold()


def _nutrition_focus(ingredient_links):
    names = [link.ingredient.name.casefold() for link in ingredient_links]
    return [
        focus for focus, hints in INGREDIENT_HINTS.items()
        if any(hint in name for hint in hints for name in names)
    ]


def _format_meal(meal, ingredient_links):
    ingredients = [
        {
            "name": link.ingredient.name,
            "quantity": str(link.quantity) if link.quantity is not None else None,
            "unit": link.unit or link.ingredient.default_unit,
        }
        for link in ingredient_links
    ]
    if meal.preparation_minutes is None:
        preparation = "No preparation time is saved; refer to the meal's stored description."
    else:
        preparation = (
            f"Allow about {meal.preparation_minutes} minutes and refer to the meal's stored description."
        )
    return {
        "id": meal.id,
        "name": meal.name,
        "meal_type": meal.meal_type,
        "description": meal.description,
        "preparation_minutes": meal.preparation_minutes,
        "servings": meal.servings,
        "ingredients": ingredients,
        "nutrition_focus": _nutrition_focus(ingredient_links),
        "preparation_guidance": preparation,
    }


def _build_grocery_list(planned_meals):
    grouped = {}
    for meal in planned_meals:
        for link in _meal_ingredients(meal):
            unit = link.unit or link.ingredient.default_unit
            key = (link.ingredient_id, unit.casefold())
            entry = grouped.setdefault(key, {
                "ingredient": link.ingredient.name,
                "quantity": Decimal("0"),
                "has_unknown_quantity": False,
                "unit": unit,
                "planned_occurrences": 0,
            })
            entry["planned_occurrences"] += 1
            if link.quantity is None:
                entry["has_unknown_quantity"] = True
            else:
                entry["quantity"] += link.quantity

    grocery_list = []
    for entry in sorted(grouped.values(), key=lambda item: item["ingredient"].casefold()):
        quantity = None if entry["has_unknown_quantity"] else str(entry["quantity"])
        grocery_list.append({
            "ingredient": entry["ingredient"],
            "quantity": quantity,
            "unit": entry["unit"],
            "planned_occurrences": entry["planned_occurrences"],
        })
    return grocery_list


def generate_weekly_plan(profile_id, week_start):
    """Build seven days from profile meals; return an explanation when slots lack data."""
    preferences = list(
        FoodPreference.objects.filter(
            profile_id=profile_id,
            preference_type__in=(FoodPreference.PreferenceType.LIKES, FoodPreference.PreferenceType.AVOIDS),
        ).order_by("preference_type", "name")
    )
    likes = [pref.name.casefold().strip() for pref in preferences if pref.preference_type == FoodPreference.PreferenceType.LIKES]
    avoids = [pref.name.casefold().strip() for pref in preferences if pref.preference_type == FoodPreference.PreferenceType.AVOIDS]

    meals = list(
        Meal.objects.filter(profile_id=profile_id, meal_type__in=SLOT_TYPES)
        .prefetch_related("ingredients")
        .order_by("name", "id")
    )
    eligible_by_type = defaultdict(list)
    for meal in meals:
        links = _meal_ingredients(meal)
        text = _meal_text(meal, links)
        if any(term and term in text for term in avoids):
            continue
        like_score = sum(1 for term in likes if term and term in text)
        eligible_by_type[meal.meal_type].append((like_score, meal, links))

    missing_slots = [
        slot for slot in REQUIRED_TYPES if not eligible_by_type[slot]
    ]
    if missing_slots:
        return {
            "plan_available": False,
            "week_start": week_start.isoformat(),
            "week_end": (week_start + timedelta(days=6)).isoformat(),
            "missing_meal_types": missing_slots,
            "explanation": (
                "A complete seven-day plan needs at least one stored, non-avoided breakfast, lunch, "
                "and dinner for this profile. Add matching meals or review avoid preferences."
            ),
            "weekly_plan": [],
            "grocery_list": [],
            "budget": {
                "available": False,
                "estimated_daily": None,
                "estimated_weekly": None,
                "reason": "Meal and ingredient models do not store prices or budget amounts.",
            },
        }

    for slot in eligible_by_type:
        eligible_by_type[slot].sort(key=lambda value: (-value[0], value[1].name.casefold(), value[1].id))

    weekly_plan = []
    grocery_meals = []
    for day_index in range(7):
        plan_date = week_start + timedelta(days=day_index)
        day_meals = {}
        for slot_index, slot in enumerate(SLOT_TYPES):
            candidates = eligible_by_type.get(slot, [])
            if not candidates:
                day_meals[slot] = None
                continue
            # Rotate through saved options over the week while liked matches rank first.
            like_count = sum(1 for score, _, _ in candidates if score > 0)
            offset = day_index % (like_count or len(candidates))
            ranked = candidates[:like_count] if like_count else candidates
            _, meal, links = ranked[(offset + slot_index) % len(ranked)]
            day_meals[slot] = _format_meal(meal, links)
            grocery_meals.append(meal)
        weekly_plan.append({"date": plan_date.isoformat(), "meals": day_meals})

    return {
        "plan_available": True,
        "week_start": week_start.isoformat(),
        "week_end": (week_start + timedelta(days=6)).isoformat(),
        "missing_meal_types": [],
        "weekly_plan": weekly_plan,
        "grocery_list": _build_grocery_list(grocery_meals),
        "budget": {
            "available": False,
            "estimated_daily": None,
            "estimated_weekly": None,
            "reason": "Meal and ingredient models do not store prices or budget amounts.",
        },
        "preferences_applied": {
            "likes_used_to_prioritize": likes,
            "avoided_terms_excluded": avoids,
            "note": "Stored likes rank matching meals first; stored avoids exclude matching meal names, descriptions, or ingredient names.",
        },
        "nutrition_note": (
            "Protein, healthy-fat, and fibre/vegetable tags are simple matches against stored ingredient names. "
            "They are general planning hints, not nutrition analysis or medical advice."
        ),
        "saved": False,
        "preparation_note": "Preparation guidance uses saved preparation times and descriptions; no cooking steps are invented.",
    }
