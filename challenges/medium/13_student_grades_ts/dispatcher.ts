export function buildHandlers(
  eventTypes: string[]
): Record<string, (payload: any) => { event: string; data: any }> {
  const handlers: Record<string, (payload: any) => any> = {};
  for (var event of eventTypes) {    // bug: var, not let
    handlers[event] = (payload: any) => ({ event: event, data: payload });
  }
  return handlers;
}
