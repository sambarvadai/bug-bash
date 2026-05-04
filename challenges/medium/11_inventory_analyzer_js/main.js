const { filterActive, summarize } = require('./processor');

function analyzeInventory(items) {
  const active = filterActive(items);
  const values = [...active].map(item => item.value);      // first spread exhausts the generator
  const activeNames = [...active].map(item => item.name);  // bug: second spread yields nothing
  return {
    active_names: activeNames,
    stats: summarize(values),
  };
}

module.exports = { analyzeInventory };
