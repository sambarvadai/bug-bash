import { buildHandlers } from './dispatcher';

interface Event { type: string; payload: any; }

export function processEvents(events: Event[]): { event: string; data: any }[] {
  const seen = new Set<string>();
  const uniqueTypes: string[] = [];
  for (const e of events) {
    if (!seen.has(e.type)) { uniqueTypes.push(e.type); seen.add(e.type); }
  }
  const handlers = buildHandlers(uniqueTypes);
  return events.map(e => handlers[e.type](e.payload));
}
