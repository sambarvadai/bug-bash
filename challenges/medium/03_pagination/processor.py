def normalize(records):
    """
    Scale each record's 'value' to the range [0.0, 1.0]
    using the maximum value in the set as the divisor.
    Returns the normalized records.
    """
    if not records:
        return records
    max_val = max(r["value"] for r in records)
    if max_val == 0:
        return records
    for record in records:
        record["value"] = round(record["value"] / max_val, 2)
    return records
