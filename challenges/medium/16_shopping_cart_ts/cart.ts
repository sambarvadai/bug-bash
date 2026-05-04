interface Item { name: string; price: number; qty: number; }

export class Cart {
  customerName: string;

  constructor(customerName: string) {
    this.customerName = customerName;
    // bug: forgot this.items = [] here
  }

  addItem(name: string, price: number, qty: number = 1): void {
    (this as any).items.push({ name, price, qty });
  }

  applyDiscount(percent: number): void {
    // TODO: reduce each item's unit price by percent %
  }

  total(): number {
    return Math.round((this as any).items.reduce((s: number, i: Item) => s + i.price * i.qty, 0) * 100) / 100;
  }
}

(Cart.prototype as any).items = [];    // bug: prototype-level, shared across all instances
