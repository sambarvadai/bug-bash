from dispatcher import build_handlers


def process_events(events):
    """
    events: list of {"type": str, "payload": any}

    Builds a handler for each unique event type, then applies
    the matching handler to every event in order.

    Returns a list of {"event": str, "data": any} dicts.
    """
    unique_types = []
    seen = set()
    for e in events:
        if e["type"] not in seen:
            unique_types.append(e["type"])
            seen.add(e["type"])

    handlers = build_handlers(unique_types)
    return [handlers[e["type"]](e["payload"]) for e in events]
