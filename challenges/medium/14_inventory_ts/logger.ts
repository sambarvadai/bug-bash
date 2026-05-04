const log: string[] = [];    // bug: module-level, shared across every RequestLog instance

export class RequestLog {
  serviceName: string;

  constructor(serviceName: string) {
    this.serviceName = serviceName;
  }

  record(requestId: string): void {
    log.push(requestId);
  }

  getLog(): string[] {
    return [...log];
  }
}
