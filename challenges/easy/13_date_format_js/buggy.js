function daysBetween(startStr, endStr) {
  const parseDate = str => {
    const parts = str.split('/');
    return new Date(parts[2], parts[0] - 1, parts[1]);
  };
  const start = parseDate(startStr);
  const end = parseDate(endStr);
  return Math.round((end - start) / (1000 * 60 * 60 * 24));
}

module.exports = { daysBetween };
