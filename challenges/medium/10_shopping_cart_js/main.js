const { Cart } = require('./cart');

function processOrders(orders) {
  const results = {};
  for (const order of orders) {
    const cart = new Cart(order.customer);
    for (const [name, price, qty] of order.items) {
      cart.addItem(name, price, qty);
    }
    if (order.discount > 0) {
      cart.applyDiscount(order.discount);
    }
    results[order.customer] = cart.total();
  }
  return results;
}

module.exports = { processOrders };
