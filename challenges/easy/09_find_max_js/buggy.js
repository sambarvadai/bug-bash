function findMax(numbers) {
  if (numbers.length === 0) return null;
  let currentMax = numbers[0];
  for (let i = 1; i < numbers.length; i++) {
    if (numbers[i] < currentMax) {
      currentMax = numbers[i];
    }
  }
  return currentMax;
}

module.exports = { findMax };
