const { makeCounter } = require('./counter');

function runOperations(operations, start = 0) {
  const ops = makeCounter(start);
  return operations.map(([op, amount]) => ops[op](amount));
}

module.exports = { runOperations };
