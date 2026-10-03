from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.body_shape.models import BodyMeasurement, Profile
from apps.diet.models import FoodPreference, Ingredient, Meal, MealIngredient, MealPlan, MealPlanItem
from apps.expenses.models import BudgetCategory, Expense, Income
from apps.lifestyle.models import DailyPlan
from apps.outfits.models import Outfit, OutfitItem
from apps.tracking.models import DailyTracking
from apps.wardrobe.models import WardrobeItem


class Command(BaseCommand):
    help = "Create or reuse realistic development records for the demo profile."

    MODULES = (
        "Profile", "Body measurements", "Meals", "Meal plans", "Wardrobe",
        "Outfits", "Budget categories", "Expenses", "Income", "Daily plans", "Tracking",
    )

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo", help="Username to create if no Demo User profile exists.")

    @transaction.atomic
    def handle(self, *args, **options):
        self.totals = {name: {"created": 0, "reused": 0} for name in self.MODULES}
        today = timezone.localdate()
        user, profile = self._get_demo_profile(options["username"])
        self._seed_measurements(profile, today)
        meals = self._seed_meals(profile)
        meal_plans = self._seed_meal_plans(profile, meals, today)
        wardrobe = self._seed_wardrobe(profile)
        outfits = self._seed_outfits(profile, wardrobe)
        categories = self._seed_categories(profile)
        daily_plans = self._seed_daily_plans(profile, meal_plans, outfits, today)
        self._seed_expenses(profile, categories, daily_plans, today)
        self._seed_income(profile, today)
        self._seed_tracking(profile, daily_plans, today)

        self.stdout.write(self.style.SUCCESS("Demo data ready; existing records were preserved."))
        for module in self.MODULES:
            counts = self.totals[module]
            self.stdout.write(f"{module}: created {counts['created']}, reused {counts['reused']}")

    def _record(self, module, created):
        self.totals[module]["created" if created else "reused"] += 1

    def _ensure(self, module, model, lookup, defaults=None):
        obj, created = model.objects.get_or_create(**lookup, defaults=defaults or {})
        self._record(module, created)
        return obj

    def _get_demo_profile(self, username):
        profile = Profile.objects.select_related("user").filter(display_name__iexact="Demo User").order_by("id").first()
        if profile:
            self._record("Profile", False)
            return profile.user, profile

        User = get_user_model()
        user = User.objects.filter(username__iexact="demo").first() or User.objects.filter(username__iexact="demo_user").first()
        if user is None:
            if User.objects.filter(username__iexact=username).exists():
                raise CommandError(
                    f"Username '{username}' already belongs to an account that is not marked as the demo user. "
                    "Choose another username with --username."
                )
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": "Demo", "last_name": "User", "email": ""},
            )
            if user_created:
                user.set_unusable_password()
                user.save(update_fields=["password"])
        profile, created = Profile.objects.get_or_create(
            user=user, defaults={"display_name": "Demo User", "currency_code": "INR"}
        )
        self._record("Profile", created)
        return user, profile

    def _seed_measurements(self, profile, today):
        measurements = (
            (45, {"height_cm": "165.00", "shoulder_cm": "38.00", "bust_cm": "90.00", "waist_cm": "72.00", "hip_cm": "98.00", "styling_shape": BodyMeasurement.StylingShape.PEAR, "approximate_size_notes": "Demo reference only"}),
            (7, {"height_cm": "165.00", "shoulder_cm": "39.00", "bust_cm": "91.00", "waist_cm": "73.00", "hip_cm": "97.00", "styling_shape": BodyMeasurement.StylingShape.HOURGLASS, "approximate_size_notes": "Demo reference only"}),
        )
        for days_ago, values in measurements:
            self._ensure("Body measurements", BodyMeasurement,
                         {"profile": profile, "measured_on": today - timedelta(days=days_ago)}, values)

    def _seed_meals(self, profile):
        ingredient_units = {
            "Rolled oats": "g", "Banana": "piece", "Milk": "ml", "Rice": "g",
            "Lentils": "g", "Tomato": "piece", "Paneer": "g", "Spinach": "g",
            "Whole wheat flour": "g", "Yogurt": "g",
        }
        ingredients = {
            name: self._ensure("Meals", Ingredient, {"name": name}, {"default_unit": unit})
            for name, unit in ingredient_units.items()
        }
        data = (
            ("Demo Oat and Banana Bowl", Meal.MealType.BREAKFAST, "Oats with banana and milk.", 10, [("Rolled oats", "60.00"), ("Banana", "1.00"), ("Milk", "200.00")]),
            ("Demo Vegetable Poha", Meal.MealType.BREAKFAST, "A simple poha breakfast with tomato.", 20, [("Tomato", "1.00")]),
            ("Demo Lentil Rice Bowl", Meal.MealType.LUNCH, "Rice served with lentils and tomato.", 35, [("Rice", "100.00"), ("Lentils", "70.00"), ("Tomato", "1.00")]),
            ("Demo Spinach Paneer Wrap", Meal.MealType.LUNCH, "Paneer and spinach with whole wheat flatbread.", 25, [("Paneer", "100.00"), ("Spinach", "50.00"), ("Whole wheat flour", "60.00")]),
            ("Demo Paneer Spinach Curry", Meal.MealType.DINNER, "A home-style paneer and spinach curry.", 30, [("Paneer", "120.00"), ("Spinach", "70.00"), ("Tomato", "1.00")]),
            ("Demo Lentil Tomato Soup", Meal.MealType.DINNER, "Lentil soup with tomato and yogurt on the side.", 30, [("Lentils", "80.00"), ("Tomato", "2.00"), ("Yogurt", "80.00")]),
        )
        meals = {}
        for name, meal_type, description, minutes, recipe in data:
            meal = self._ensure("Meals", Meal, {"profile": profile, "name": name},
                                {"meal_type": meal_type, "description": description, "preparation_minutes": minutes, "servings": 1})
            meals[name] = meal
            for ingredient_name, quantity in recipe:
                ingredient = ingredients[ingredient_name]
                self._ensure("Meals", MealIngredient, {"meal": meal, "ingredient": ingredient},
                             {"quantity": Decimal(quantity), "unit": ingredient.default_unit})
        for preference_type, name in (
            (FoodPreference.PreferenceType.LIKES, "oats"),
            (FoodPreference.PreferenceType.LIKES, "lentil"),
            (FoodPreference.PreferenceType.AVOIDS, "Demo unavailable ingredient"),
        ):
            self._ensure("Meals", FoodPreference,
                         {"profile": profile, "preference_type": preference_type, "name": name},
                         {"notes": "Development demonstration preference"})
        return meals

    def _seed_meal_plans(self, profile, meals, today):
        choices = {
            MealPlanItem.MealSlot.BREAKFAST: ["Demo Oat and Banana Bowl", "Demo Vegetable Poha"],
            MealPlanItem.MealSlot.LUNCH: ["Demo Lentil Rice Bowl", "Demo Spinach Paneer Wrap"],
            MealPlanItem.MealSlot.DINNER: ["Demo Paneer Spinach Curry", "Demo Lentil Tomato Soup"],
        }
        plans = {}
        for index in range(7):
            day = today - timedelta(days=6 - index)
            plan = self._ensure("Meal plans", MealPlan, {"profile": profile, "plan_date": day},
                                {"notes": "Demo weekly meal plan"})
            plans[day] = plan
            for slot, names in choices.items():
                self._ensure("Meal plans", MealPlanItem,
                             {"meal_plan": plan, "slot": slot, "meal": meals[names[index % len(names)]]},
                             {"is_completed": index < 4})
        return plans

    def _seed_wardrobe(self, profile):
        data = (
            ("Demo blue cotton shirt", WardrobeItem.Category.TOP, "blue", WardrobeItem.Status.AVAILABLE),
            ("Demo white linen shirt", WardrobeItem.Category.TOP, "white", WardrobeItem.Status.AVAILABLE),
            ("Demo green casual top", WardrobeItem.Category.TOP, "green", WardrobeItem.Status.AVAILABLE),
            ("Demo navy trousers", WardrobeItem.Category.BOTTOM, "navy", WardrobeItem.Status.AVAILABLE),
            ("Demo beige chinos", WardrobeItem.Category.BOTTOM, "beige", WardrobeItem.Status.AVAILABLE),
            ("Demo charcoal skirt", WardrobeItem.Category.BOTTOM, "charcoal", WardrobeItem.Status.AVAILABLE),
            ("Demo floral day dress", WardrobeItem.Category.DRESS, "floral", WardrobeItem.Status.AVAILABLE),
            ("Demo light jacket", WardrobeItem.Category.OUTERWEAR, "tan", WardrobeItem.Status.AVAILABLE),
            ("Demo walking shoes", WardrobeItem.Category.SHOES, "white", WardrobeItem.Status.AVAILABLE),
            ("Demo leather belt", WardrobeItem.Category.ACCESSORY, "brown", WardrobeItem.Status.AVAILABLE),
            ("Demo laundry sweater", WardrobeItem.Category.TOP, "grey", WardrobeItem.Status.LAUNDRY),
        )
        return {name: self._ensure("Wardrobe", WardrobeItem,
                                   {"profile": profile, "name": name, "color": color},
                                   {"category": category, "status": status, "brand": "", "size_label": "", "notes": "Development demonstration item"})
                for name, category, color, status in data}

    def _seed_outfits(self, profile, wardrobe):
        data = (
            ("Demo everyday look", Outfit.Occasion.EVERYDAY, [("Demo blue cotton shirt", OutfitItem.Slot.TOP), ("Demo navy trousers", OutfitItem.Slot.BOTTOM), ("Demo walking shoes", OutfitItem.Slot.SHOES), ("Demo light jacket", OutfitItem.Slot.OUTERWEAR)]),
            ("Demo work look", Outfit.Occasion.WORK, [("Demo white linen shirt", OutfitItem.Slot.TOP), ("Demo beige chinos", OutfitItem.Slot.BOTTOM), ("Demo leather belt", OutfitItem.Slot.ACCESSORY), ("Demo walking shoes", OutfitItem.Slot.SHOES)]),
            ("Demo event look", Outfit.Occasion.EVENT, [("Demo floral day dress", OutfitItem.Slot.ONE_PIECE), ("Demo walking shoes", OutfitItem.Slot.SHOES)]),
        )
        outfits = {}
        for name, occasion, components in data:
            outfit = self._ensure("Outfits", Outfit, {"profile": profile, "name": name},
                                  {"occasion": occasion, "notes": "Development demonstration outfit"})
            outfits[name] = outfit
            for position, (item_name, slot) in enumerate(components):
                self._ensure("Outfits", OutfitItem, {"outfit": outfit, "item": wardrobe[item_name]},
                             {"slot": slot, "position": position})
        return outfits

    def _seed_categories(self, profile):
        categories = {}
        for name, limit in (("Demo Groceries", "12000.00"), ("Demo Clothing", "8000.00"), ("Demo Transport", "5000.00")):
            categories[name] = self._ensure("Budget categories", BudgetCategory,
                                            {"profile": profile, "name": name},
                                            {"monthly_limit": Decimal(limit), "is_active": True})
        return categories

    def _seed_daily_plans(self, profile, meal_plans, outfits, today):
        plans = {}
        for index in range(7):
            day = today - timedelta(days=6 - index)
            name = "Demo work look" if day.weekday() < 5 else "Demo everyday look"
            plans[day] = self._ensure(
                "Daily plans", DailyPlan, {"profile": profile, "plan_date": day},
                {"outfit": outfits[name], "meal_plan": meal_plans[day], "notes": "Demo plan: review meals, outfit, and daily priorities."},
            )
        return plans

    def _seed_expenses(self, profile, categories, daily_plans, today):
        records = (
            ("Demo weekly groceries", "Demo Groceries", Decimal("1850.00"), today.replace(day=max(1, today.day - 7))),
            ("Demo market vegetables", "Demo Groceries", Decimal("640.00"), today),
            ("Demo transit pass", "Demo Transport", Decimal("1200.00"), today.replace(day=1)),
            ("Demo cotton shirt purchase", "Demo Clothing", Decimal("2450.00"), today - timedelta(days=35)),
            ("Demo grocery basket", "Demo Groceries", Decimal("1725.00"), today - timedelta(days=35)),
        )
        for description, category_name, amount, spent_on in records:
            self._ensure("Expenses", Expense,
                         {"profile": profile, "category": categories[category_name], "description": description, "spent_on": spent_on},
                         {"amount": amount, "daily_plan": daily_plans.get(spent_on), "notes": "Development demonstration record"})

    def _seed_income(self, profile, today):
        month_start = today.replace(day=1)
        previous_month_last = month_start - timedelta(days=1)
        data = (
            ("Demo monthly stipend", Decimal("30000.00"), month_start),
            ("Demo freelance payment", Decimal("6500.00"), today),
            ("Demo previous month stipend", Decimal("30000.00"), previous_month_last.replace(day=min(today.day, previous_month_last.day))),
        )
        for source, amount, received_on in data:
            self._ensure("Income", Income, {"profile": profile, "source": source, "received_on": received_on},
                         {"amount": amount, "notes": "Development demonstration record"})

    def _seed_tracking(self, profile, daily_plans, today):
        for index in range(7):
            day = today - timedelta(days=6 - index)
            self._ensure("Tracking", DailyTracking, {"profile": profile, "track_date": day},
                         {"daily_plan": daily_plans[day], "outfit_completed": index % 2 == 0,
                          "meals_completed": index < 5, "expenses_reviewed": index in (1, 3, 5),
                          "daily_plan_completed": index < 4, "notes": "Demo check-in" if index < 4 else ""})
