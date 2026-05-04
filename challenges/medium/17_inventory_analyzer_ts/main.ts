import { filterActive, summarize } from './processor';

export function analyzeInventory(items: any[]) {
  const active = filterActive(items);
  const values = [...active].map((item: any) => item.value);      // first spread exhausts the generator
  const activeNames = [...active].map((item: any) => item.name);  // bug: second spread yields nothing
  return {
    active_names: activeNames,
    stats: summarize(values),
  };
}
