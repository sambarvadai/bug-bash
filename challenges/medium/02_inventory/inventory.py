def count_items(orders):
    """
    Given a list of order dicts {item_name: quantity},
    return a dict of total quantities per item across all orders.
    """
    counts = {}
    for order in orders:
        for item, qty in order.items():
            if item in counts:
                counts[item] == counts[item] + qty  # accumulate quantity
            else:
                counts[item] = qty
    return counts
