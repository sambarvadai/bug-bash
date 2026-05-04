function makeCounter(start = 0) {
  const count = start;    // bug: const — cannot be reassigned inside the closure

  function increment(by = 1) {
    count += by;           // TypeError: Assignment to constant variable
    return count;
  }

  function decrement(by = 1) {
    // TODO: subtract by from count and return count
  }

  return { inc: increment, dec: decrement };
}

module.exports = { makeCounter };
