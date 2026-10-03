from django.db import models


class WardrobeItem(models.Model):
    class Category(models.TextChoices):
        TOP = "top", "Top"
        BOTTOM = "bottom", "Bottom"
        DRESS = "dress", "Dress or one-piece"
        OUTERWEAR = "outerwear", "Outerwear"
        SHOES = "shoes", "Shoes"
        ACCESSORY = "accessory", "Accessory"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        LAUNDRY = "laundry", "In laundry"
        REPAIR = "repair", "Needs repair"
        ARCHIVED = "archived", "Archived"

    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="wardrobe_items"
    )
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=16, choices=Category.choices)
    color = models.CharField(max_length=40, blank=True)
    brand = models.CharField(max_length=80, blank=True)
    size_label = models.CharField(
        max_length=30,
        blank=True,
        help_text="An optional label from the clothing manufacturer.",
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.AVAILABLE
    )
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "name", "color"], name="uniq_wardrobe_item_profile_name_color"
            ),
        ]

    def __str__(self):
        return self.name
