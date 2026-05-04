function normalize(records) {
  if (!records.length) return records;
  const maxVal = Math.max(...records.map(r => r.value));
  if (maxVal === 0) return records;
  for (const record of records) {
    record.value = Math.round((record.value / maxVal) * 100) / 100;   // bug: mutates in place
  }
  return records;
}

module.exports = { normalize };
