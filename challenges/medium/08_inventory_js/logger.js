const log = [];    // bug: module-level array, shared across every RequestLog instance

class RequestLog {
  constructor(serviceName) {
    this.serviceName = serviceName;
  }

  record(requestId) {
    log.push(requestId);
  }

  getLog() {
    return [...log];
  }
}

module.exports = { RequestLog };
