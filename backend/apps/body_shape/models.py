from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Profile(models.Model):
    """Personal preferences that belong to one Django account."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lifestyle_profile",
    )
    display_name = models.CharField(max_length=80, blank=True)
    currency_code = models.CharField(max_length=3, default="INR")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_name", "id"]

    def __str__(self):
        return self.display_name or self.user.get_username()


class BodyMeasurement(models.Model):
    """Optional measurements saved for approximate clothing and styling guidance."""

    class StylingShape(models.TextChoices):
        HOURGLASS = "hourglass", "Hourglass"
        PEAR = "pear", "Pear"
        APPLE = "apple", "Apple"
        RECTANGLE = "rectangle", "Rectangle"
        INVERTED_TRIANGLE = "inverted_triangle", "Inverted triangle"
        NOT_SET = "not_set", "Not selected"

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="body_measurements"
    )
    measured_on = models.DateField()
    height_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(300)],
    )
    shoulder_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(300)],
    )
    bust_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(300)],
    )
    waist_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(300)],
    )
    hip_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(300)],
    )
    styling_shape = models.CharField(
        max_length=24,
        choices=StylingShape.choices,
        default=StylingShape.NOT_SET,
        help_text="Optional approximate styling label; this is not a medical assessment.",
    )
    approximate_size_notes = models.CharField(
        max_length=160,
        blank=True,
        help_text="Optional clothing-size notes for styling reference only.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-measured_on", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "measured_on"], name="uniq_measurement_profile_day"
            ),
        ]

    def __str__(self):
        return f"Measurements for {self.profile} on {self.measured_on}"
