function buildHandlers(eventTypes) {
  const handlers = {};
  for (var event of eventTypes) {    // bug: var, not let — all closures share the same binding
    handlers[event] = (payload) => ({ event: event, data: payload });
  }
  return handlers;
}

module.exports = { buildHandlers };
