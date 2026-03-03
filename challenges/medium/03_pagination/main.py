from processor import normalize


def summarize(raw_records):
    """
    raw_records: list of {"name": str, "value": int}

    Returns:
        {
            "original":   [values before normalization],
            "normalized": [values after normalization, 0.0–1.0],
            "top":        name of the record with the highest original value
        }
    """
    top = max(raw_records, key=lambda r: r["value"])["name"]
    normalized = normalize(raw_records)
    return {
        "original":   [r["value"] for r in raw_records],
        "normalized": [r["value"] for r in normalized],
        "top": top,
    }
