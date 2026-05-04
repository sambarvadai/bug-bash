export function makeCounter(start: number = 0): Record<string, (by: number) => number> {
  const count = start;    // bug: const — cannot be reassigned

  function increment(by: number = 1): number {
    (count as any) += by;   // TypeError at runtime: Assignment to constant variable
    return count;
  }

  function decrement(by: number = 1): number {
    // TODO: subtract by from count and return count
    return 0;
  }

  return { inc: increment, dec: decrement };
}
