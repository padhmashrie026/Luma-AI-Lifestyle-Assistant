"""Simple, transparent styling guidance based on measurement proportions."""


STYLING_SUGGESTIONS = {
    "hourglass": "Try styles that follow the waist while keeping the upper and lower silhouette balanced.",
    "pear": "Try drawing attention to the upper body with balanced colors, necklines, or structured layers.",
    "apple": "Try comfortable waist-skimming layers and use proportions or details to define the silhouette.",
    "rectangle": "Try layers, belts, or contrasting pieces to create visual definition around the waist.",
    "inverted_triangle": "Try simpler upper-body lines with visual detail, color, or volume near the hips.",
}


def calculate_body_shape(shoulder, bust, waist, hip):
    """Return an approximate styling label using broad ratio thresholds."""
    upper = max(shoulder, bust)
    lower = hip

    if waist <= upper * 0.75 and waist <= lower * 0.75 and 0.90 <= upper / lower <= 1.10:
        shape = "hourglass"
    elif lower > upper * 1.05:
        shape = "pear"
    elif upper > lower * 1.05:
        shape = "inverted_triangle"
    elif waist >= max(upper, lower) * 0.90:
        shape = "apple"
    else:
        shape = "rectangle"

    return {
        "estimated_body_shape": shape,
        "styling_suggestion": STYLING_SUGGESTIONS[shape],
        "approximate_size_guidance": (
            "Compare your measurements with the specific brand's size chart; sizing varies, "
            "so use the largest relevant measurement as a starting point."
        ),
        "note": "This is approximate rule-based styling guidance, not a scientific or medical diagnosis.",
    }
