def filter_active(items):
    """Return only the items where active=True."""
    return (item for item in items if item["active"])  # something subtle here


def summarize(values):
    """
    Given a list of numeric values, return basic statistics.
    Returns {"count": n, "total": sum, "average": avg}.
    If values is empty, return {"count": 0, "total": 0, "average": 0}.
    """
    pass  # TODO: implement
