export function* filterActive(items: any[]): Generator<any> {    // bug: generator
  for (const item of items) {
    if (item.active) yield item;
  }
}

export function summarize(values: number[]): { count: number; total: number; average: number } | undefined {
  // TODO: return { count, total, average } — for empty input return all zeros
}
