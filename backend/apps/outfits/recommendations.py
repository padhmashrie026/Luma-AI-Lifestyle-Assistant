"""Transparent rules for building an outfit from a profile's stored wardrobe."""

from apps.body_shape.models import BodyMeasurement
from apps.body_shape.calculations import STYLING_SUGGESTIONS
from apps.wardrobe.models import WardrobeItem

from .models import Outfit


def _complete_combination(items):
    by_category = {}
    for item in items:
        by_category.setdefault(item.category, []).append(item)

    one_piece = by_category.get(WardrobeItem.Category.DRESS)
    if one_piece:
        return {"selected_one_piece": one_piece[0], "selected_top": None, "selected_bottom": None}

    tops = by_category.get(WardrobeItem.Category.TOP, [])
    bottoms = by_category.get(WardrobeItem.Category.BOTTOM, [])
    if tops and bottoms:
        return {"selected_one_piece": None, "selected_top": tops[0], "selected_bottom": bottoms[0]}
    return None


def _latest_saved_shape(profile_id):
    measurement = (
        BodyMeasurement.objects.filter(profile_id=profile_id)
        .exclude(styling_shape=BodyMeasurement.StylingShape.NOT_SET)
        .order_by("-measured_on", "-id")
        .first()
    )
    return measurement.styling_shape if measurement else None


def recommend_outfit(profile_id, occasion, body_shape=None):
    """Use available wardrobe items, preferring a complete saved look for occasion."""
    available = list(
        WardrobeItem.objects.filter(
            profile_id=profile_id,
            status=WardrobeItem.Status.AVAILABLE,
        ).order_by("category", "name", "id")
    )
    shape = body_shape or _latest_saved_shape(profile_id)
    matched_outfit = None
    combination = None

    saved_looks = Outfit.objects.filter(profile_id=profile_id, occasion=occasion).order_by("name", "id")
    available_ids = {item.id for item in available}
    for saved_look in saved_looks:
        look_items = [item for item in saved_look.items.all() if item.id in available_ids]
        combination = _complete_combination(look_items)
        if combination:
            matched_outfit = saved_look
            break

    occasion_used = matched_outfit is not None
    source_items = (
        [item for item in matched_look_items(matched_outfit) if item.id in available_ids]
        if matched_outfit else available
    )
    combination = _complete_combination(source_items)

    if combination:
        selected = {
            **combination,
            "selected_outerwear": next(
                (item for item in source_items if item.category == WardrobeItem.Category.OUTERWEAR), None
            ),
            "selected_accessory": next(
                (item for item in source_items if item.category == WardrobeItem.Category.ACCESSORY), None
            ),
        }
        missing = []
    else:
        categories = {item.category for item in available}
        missing = []
        if WardrobeItem.Category.DRESS not in categories:
            if WardrobeItem.Category.TOP not in categories:
                missing.append("top")
            if WardrobeItem.Category.BOTTOM not in categories:
                missing.append("bottom")
        selected = {
            "selected_one_piece": None,
            "selected_top": None,
            "selected_bottom": None,
            "selected_outerwear": None,
            "selected_accessory": None,
        }

    explanation_parts = [
        "Only wardrobe items marked available for this profile were considered."
    ]
    if occasion_used:
        explanation_parts.append(
            f"The selected pieces come from the saved {matched_outfit.get_occasion_display().lower()} outfit '{matched_outfit.name}'."
        )
    else:
        explanation_parts.append(
            "No complete saved outfit for this occasion was available, so the pieces were paired by clothing category. "
            "Individual wardrobe items do not store an occasion."
        )
    if shape:
        explanation_parts.append(
            f"The approximate {shape.replace('_', ' ')} styling label is used for general guidance: "
            f"{STYLING_SUGGESTIONS.get(shape, 'Use personal styling preferences when choosing a look')}"
        )
    else:
        explanation_parts.append(
            "No body shape was supplied or saved, so the recommendation uses clothing categories only."
        )

    return {
        "recommendation_available": combination is not None,
        "profile_id": profile_id,
        "occasion": occasion,
        "body_shape": shape,
        "season_applied": False,
        "missing_items": missing,
        "recommendation": selected if combination else None,
        "message": (
            "A wardrobe-based outfit is ready."
            if combination
            else f"Not enough available items to build an outfit. Add an available {' and '.join(missing)} or a one-piece item."
        ),
        "explanation": " ".join(explanation_parts),
    }


def matched_look_items(look):
    """Fetch items for one saved look in predictable category/name order."""
    return list(look.items.order_by("category", "name", "id"))
