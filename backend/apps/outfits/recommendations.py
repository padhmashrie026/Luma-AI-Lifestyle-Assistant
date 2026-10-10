"""Transparent rules for building an outfit from a profile's stored wardrobe."""

from itertools import product

from apps.body_shape.models import BodyMeasurement
from apps.body_shape.calculations import STYLING_SUGGESTIONS
from apps.wardrobe.models import WardrobeItem

from .models import Outfit


def _combinations(items):
    """Return distinct complete looks using only the supplied wardrobe items."""
    by_category = {}
    for item in items:
        by_category.setdefault(item.category, []).append(item)

    bases = [
        {"selected_one_piece": dress, "selected_top": None, "selected_bottom": None}
        for dress in by_category.get(WardrobeItem.Category.DRESS, [])
    ]
    bases.extend(
        {"selected_one_piece": None, "selected_top": top, "selected_bottom": bottom}
        for top in by_category.get(WardrobeItem.Category.TOP, [])
        for bottom in by_category.get(WardrobeItem.Category.BOTTOM, [])
    )

    combinations = []
    seen = set()
    for base in bases:
        combination = {**base, "selected_outerwear": None, "selected_accessory": None}
        combinations.append(combination)
        seen.add(tuple(combination[field].id if combination[field] else None for field in (
            "selected_one_piece", "selected_top", "selected_bottom", "selected_outerwear", "selected_accessory"
        )))
    layers = [None, *by_category.get(WardrobeItem.Category.OUTERWEAR, [])]
    accessories = [None, *by_category.get(WardrobeItem.Category.ACCESSORY, [])]
    for base in bases:
        for outerwear, accessory in product(layers, accessories):
            if outerwear is None and accessory is None:
                continue
            combination = {**base, "selected_outerwear": outerwear, "selected_accessory": accessory}
            key = tuple(combination[field].id if combination[field] else None for field in (
                "selected_one_piece", "selected_top", "selected_bottom", "selected_outerwear", "selected_accessory"
            ))
            if key not in seen:
                combinations.append(combination)
                seen.add(key)
                if len(combinations) == 5:
                    return combinations
    return combinations


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
    wardrobe_empty = not WardrobeItem.objects.filter(profile_id=profile_id).exists()
    available = list(
        WardrobeItem.objects.filter(
            profile_id=profile_id,
            status=WardrobeItem.Status.AVAILABLE,
        ).order_by("category", "name", "id")
    )
    shape = body_shape or _latest_saved_shape(profile_id)
    matched_outfit = None
    combinations = []

    saved_looks = Outfit.objects.filter(profile_id=profile_id, occasion=occasion).order_by("name", "id")
    available_ids = {item.id for item in available}
    for saved_look in saved_looks:
        look_items = [item for item in saved_look.items.all() if item.id in available_ids]
        look_combinations = _combinations(look_items)
        if look_combinations:
            matched_outfit = saved_look
            combinations.extend(look_combinations)
            break

    occasion_used = matched_outfit is not None
    source_items = available
    combinations.extend(_combinations(source_items))
    unique_combinations = []
    seen_keys = set()
    for combination in combinations:
        key = tuple(
            combination[field].id if combination[field] else None
            for field in ("selected_one_piece", "selected_top", "selected_bottom", "selected_outerwear", "selected_accessory")
        )
        if key not in seen_keys:
            unique_combinations.append(combination)
            seen_keys.add(key)
    combinations = unique_combinations[:5]

    if combinations:
        selected = combinations[0]
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
        "recommendation_available": bool(combinations),
        "wardrobe_empty": wardrobe_empty,
        "profile_id": profile_id,
        "occasion": occasion,
        "body_shape": shape,
        "season_applied": False,
        "missing_items": missing,
        "recommendation": selected if combinations else None,
        "recommendations": combinations,
        "message": (
            f"Here are {len(combinations)} distinct outfit suggestion{'s' if len(combinations) != 1 else ''} from your available wardrobe."
            if combinations
            else f"Not enough available items to build an outfit. Add an available {' and '.join(missing)} or a one-piece item."
        ),
        "explanation": " ".join(explanation_parts),
    }
