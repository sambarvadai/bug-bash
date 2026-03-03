from processor import filter_active, summarize


def analyze_inventory(items):
    """
    items: list of {"name": str, "value": int, "active": bool}

    Returns:
        {
            "active_names": [names of active items, in input order],
            "stats":        {"count": n, "total": n, "average": n}
        }
    """
    active = filter_active(items)
    values = [item["value"] for item in active]
    active_names = [item["name"] for item in active]
    return {
        "active_names": active_names,
        "stats": summarize(values),
    }
