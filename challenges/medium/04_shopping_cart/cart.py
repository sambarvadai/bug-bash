class Cart:
    items = []  # store this customer's items

    def __init__(self, customer_name):
        self.customer_name = customer_name

    def add_item(self, name, price, qty=1):
        self.items.append({"name": name, "price": price, "qty": qty})

    def apply_discount(self, percent):
        pass  # TODO: reduce each item's price by percent %

    def total(self):
        return round(sum(item["price"] * item["qty"] for item in self.items), 2)
