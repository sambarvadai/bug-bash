import { RequestLog } from './logger';

interface ServiceEntry { service: string; ids: string[]; }

export function collectLogs(serviceRequests: ServiceEntry[]): Record<string, string[]> {
  const results: Record<string, string[]> = {};
  for (const entry of serviceRequests) {
    const logger = new RequestLog(entry.service);
    for (const id of entry.ids) {
      logger.record(id);
    }
    results[entry.service] = logger.getLog();
  }
  return results;
}
