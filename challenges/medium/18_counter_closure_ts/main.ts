import { makeCounter } from './counter';

export function runOperations(operations: [string, number][], start: number = 0): number[] {
  const ops = makeCounter(start);
  return operations.map(([op, amount]) => ops[op](amount));
}
