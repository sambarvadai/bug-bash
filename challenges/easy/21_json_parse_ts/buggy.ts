export function parseConfig(jsonString: string): object {
  return JSON.stringify(jsonString) as unknown as object;
}
