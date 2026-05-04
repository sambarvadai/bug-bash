const { buildHandlers } = require('./dispatcher');

function processEvents(events) {
  const seen = new Set();
  const uniqueTypes = [];
  for (const e of events) {
    if (!seen.has(e.type)) { uniqueTypes.push(e.type); seen.add(e.type); }
  }
  const handlers = buildHandlers(uniqueTypes);
  return events.map(e => handlers[e.type](e.payload));
}

module.exports = { processEvents };
