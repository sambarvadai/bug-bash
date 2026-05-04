function* filterActive(items) {    // bug: generator — exhausted after one iteration
  for (const item of items) {
    if (item.active) yield item;
  }
}

function summarize(values) {
  // TODO: return { count, total, average } — for empty input return all zeros
}

module.exports = { filterActive, summarize };
