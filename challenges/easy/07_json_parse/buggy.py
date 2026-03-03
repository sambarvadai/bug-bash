import json


def parse_config(json_string):
    """Parse a JSON-formatted string and return the resulting dict."""
    return json.load(json_string)
