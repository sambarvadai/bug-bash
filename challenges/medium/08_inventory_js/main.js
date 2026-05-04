const { RequestLog } = require('./logger');

function collectLogs(serviceRequests) {
  const results = {};
  for (const entry of serviceRequests) {
    const logger = new RequestLog(entry.service);
    for (const id of entry.ids) {
      logger.record(id);
    }
    results[entry.service] = logger.getLog();
  }
  return results;
}

module.exports = { collectLogs };
