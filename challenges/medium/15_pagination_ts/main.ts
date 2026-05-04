import { normalize } from './processor';

interface RawRecord { name: string; value: number; }

export function summarize(rawRecords: RawRecord[]) {
  const top = rawRecords.reduce((a, b) => a.value > b.value ? a : b).name;
  const normalized = normalize(rawRecords);
  return {
    original:   rawRecords.map(r => r.value),
    normalized: normalized.map(r => r.value),
    top,
  };
}
