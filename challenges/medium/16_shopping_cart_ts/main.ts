import { Cart } from './cart';

interface Order { customer: string; items: [string, number, number][]; discount: number; }

export function processOrders(orders: Order[]): Record<string, number> {
  const results: Record<string, number> = {};
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
