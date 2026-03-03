def build_handlers(event_types):
    """
    Given a list of event type names, return a dict mapping
    each event type to its handler function.

    Each handler accepts a payload and returns:
        {"event": <event_type>, "data": <payload>}
    """
    handlers = {}
    for event in event_types:
        handlers[event] = lambda payload: {"event": event, "data": payload}
    return handlers
