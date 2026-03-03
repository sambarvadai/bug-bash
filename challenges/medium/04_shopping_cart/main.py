from cart import Cart


def process_orders(orders):
    """
    orders: list of {
        "customer": str,
        "items":    [[name, price, qty], ...],
        "discount": int   (percentage, e.g. 10 = 10% off all item prices)
    }

    Returns {customer_name: total} dict.
    Each customer gets their own isolated cart.
    """
    results = {}
    for order in orders:
        cart = Cart(order["customer"])
        for name, price, qty in order["items"]:
            cart.add_item(name, price, qty)
        if order.get("discount", 0) > 0:
            cart.apply_discount(order["discount"])
        results[order["customer"]] = cart.total()
    return results
