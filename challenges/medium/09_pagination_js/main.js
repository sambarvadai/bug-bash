const { normalize } = require('./processor');

function summarize(rawRecords) {
  const top = rawRecords.reduce((a, b) => a.value > b.value ? a : b).name;
  const normalized = normalize(rawRecords);
  return {
    original:   rawRecords.map(r => r.value),    // rawRecords was mutated — these are already normalised
    normalized: normalized.map(r => r.value),
    top,
  };
}

module.exports = { summarize };
