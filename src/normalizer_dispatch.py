from src import normalizers as norm

def pick_normalizer(city_label: str):
    """
    Given a city name (from folder name), return the correct normalization function.
    This lets us keep one shared normalizer for cities with identical layouts.
    """
    key = city_label.lower().replace(" ", "").replace("-", "").replace("_", "")

    mapping = {
        "oaklandpark":  "normalize_oakland_boca",
        "bocaraton":    "normalize_oakland_boca",

        "pompano":      "normalize_pompano",

        "wiltonmanor":  "normalize_wilton",
        "wiltonmanors": "normalize_wilton",
    }

    # Default fallback if nothing matches
    fn_name = mapping.get(key, "normalize_generic")
    return getattr(norm, fn_name)
