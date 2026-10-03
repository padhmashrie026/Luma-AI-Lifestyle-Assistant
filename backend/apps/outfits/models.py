from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Outfit(models.Model):
    class Occasion(models.TextChoices):
        EVERYDAY = "everyday", "Everyday"
        WORK = "work", "Work"
        FORMAL = "formal", "Formal"
        EVENT = "event", "Event"
        OTHER = "other", "Other"

    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="outfits"
    )
    name = models.CharField(max_length=100)
    occasion = models.CharField(
        max_length=12, choices=Occasion.choices, default=Occasion.EVERYDAY
    )
    notes = models.CharField(max_length=240, blank=True)
    items = models.ManyToManyField(
        "wardrobe.WardrobeItem", through="OutfitItem", related_name="outfits"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["profile", "name"], name="uniq_outfit_profile_name")
        ]

    def __str__(self):
        return self.name


class OutfitItem(models.Model):
    class Slot(models.TextChoices):
        TOP = "top", "Top"
        BOTTOM = "bottom", "Bottom"
        ONE_PIECE = "one_piece", "Dress or one-piece"
        OUTERWEAR = "outerwear", "Outerwear"
        SHOES = "shoes", "Shoes"
        ACCESSORY = "accessory", "Accessory"
        OTHER = "other", "Other"

    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE, related_name="outfit_items")
    item = models.ForeignKey(
        "wardrobe.WardrobeItem", on_delete=models.CASCADE, related_name="outfit_items"
    )
    slot = models.CharField(max_length=12, choices=Slot.choices, default=Slot.OTHER)
    position = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ["position", "id"]
        constraints = [
            models.UniqueConstraint(fields=["outfit", "item"], name="uniq_item_per_outfit"),
        ]

    def clean(self):
        super().clean()
        if self.outfit_id and self.item_id:
            if self.outfit.profile_id != self.item.profile_id:
                raise ValidationError({"item": "Choose a wardrobe item from this profile."})

    def __str__(self):
        return f"{self.item} in {self.outfit}"
