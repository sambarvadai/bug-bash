class Cart {
  constructor(customerName) {
    this.customerName = customerName;
    // bug: forgot this.items = [] here
  }

  addItem(name, price, qty = 1) {
    this.items.push({ name, price, qty });
  }

  applyDiscount(percent) {
    // TODO: reduce each item's unit price by percent %
  }

  total() {
    return Math.round(this.items.reduce((s, i) => s + i.price * i.qty, 0) * 100) / 100;
  }
}

Cart.prototype.items = [];    // bug: prototype-level, shared across all instances

module.exports = { Cart };
