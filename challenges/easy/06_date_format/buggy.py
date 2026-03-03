import datetime


def days_between(start_str, end_str):
    """
    Given two date strings in DD/MM/YYYY format,
    return the number of days from start to end.
    """
    fmt = "%m/%d/%Y"
    start = datetime.datetime.strptime(start_str, fmt)
    end = datetime.datetime.strptime(end_str, fmt)
    return (end - start).days
