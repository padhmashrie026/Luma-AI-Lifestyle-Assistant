from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class FoodPreference(models.Model):
    class PreferenceType(models.TextChoices):
        LIKES = "likes", "Likes"
        AVOIDS = "avoids", "Avoids"
        EATING_PATTERN = "eating_pattern", "Eating pattern"
        OTHER = "other", "Other"

    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="food_preferences"
    )
    preference_type = models.CharField(max_length=16, choices=PreferenceType.choices)
    name = models.CharField(max_length=100)
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["preference_type", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "preference_type", "name"],
                name="uniq_food_preference_profile_type_name",
            ),
        ]

    def __str__(self):
        return f"{self.get_preference_type_display()}: {self.name}"


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    default_unit = models.CharField(max_length=24, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Meal(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH = "lunch", "Lunch"
        DINNER = "dinner", "Dinner"
        SNACK = "snack", "Snack"
        OTHER = "other", "Other"

    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="meals"
    )
    name = models.CharField(max_length=120)
    meal_type = models.CharField(
        max_length=12, choices=MealType.choices, default=MealType.OTHER
    )
    description = models.CharField(max_length=300, blank=True)
    preparation_minutes = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(1440)]
    )
    servings = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="MealIngredient", related_name="meals", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["profile", "name"], name="uniq_meal_profile_name")
        ]

    def __str__(self):
        return self.name


class MealIngredient(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="meal_ingredients")
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, related_name="meal_ingredients"
    )
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)],
    )
    unit = models.CharField(max_length=24, blank=True)

    class Meta:
        ordering = ["ingredient__name"]
        constraints = [
            models.UniqueConstraint(fields=["meal", "ingredient"], name="uniq_ingredient_per_meal"),
            models.CheckConstraint(
                condition=models.Q(quantity__isnull=True) | models.Q(quantity__gt=0),
                name="meal_ingredient_quantity_positive_or_empty",
            ),
        ]

    def __str__(self):
        return f"{self.ingredient} for {self.meal}"


class MealPlan(models.Model):
    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="meal_plans"
    )
    plan_date = models.DateField()
    notes = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-plan_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "plan_date"], name="uniq_meal_plan_profile_day"
            ),
        ]

    def __str__(self):
        return f"Meal plan for {self.profile} on {self.plan_date}"


class MealPlanItem(models.Model):
    class MealSlot(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH = "lunch", "Lunch"
        DINNER = "dinner", "Dinner"
        SNACK = "snack", "Snack"

    meal_plan = models.ForeignKey(
        MealPlan, on_delete=models.CASCADE, related_name="items"
    )
    meal = models.ForeignKey(Meal, on_delete=models.PROTECT, related_name="planned_items")
    slot = models.CharField(max_length=12, choices=MealSlot.choices)
    scheduled_time = models.TimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["scheduled_time", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["meal_plan", "slot", "meal"], name="uniq_meal_plan_slot_meal"
            ),
        ]

    def clean(self):
        super().clean()
        if self.meal_plan_id and self.meal_id:
            if self.meal_plan.profile_id != self.meal.profile_id:
                raise ValidationError({"meal": "Choose a meal owned by this profile."})

    def __str__(self):
        return f"{self.get_slot_display()}: {self.meal}"


class GroceryItem(models.Model):
    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="grocery_items"
    )
    meal_plan = models.ForeignKey(
        MealPlan,
        on_delete=models.SET_NULL,
        related_name="grocery_items",
        null=True,
        blank=True,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        related_name="grocery_items",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)],
    )
    unit = models.CharField(max_length=24, blank=True)
    is_purchased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["is_purchased", "name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__isnull=True) | models.Q(quantity__gt=0),
                name="grocery_quantity_positive_or_empty",
            ),
        ]

    def clean(self):
        super().clean()
        if self.meal_plan_id and self.profile_id:
            if self.meal_plan.profile_id != self.profile_id:
                raise ValidationError({"meal_plan": "Choose a meal plan from this profile."})

    def __str__(self):
        return self.name
