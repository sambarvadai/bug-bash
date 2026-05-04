export function daysBetween(startStr: string, endStr: string): number {
  const parseDate = (str: string): Date => {
    const parts = str.split('/');
    return new Date(Number(parts[2]), Number(parts[0]) - 1, Number(parts[1]));
  };
  const start = parseDate(startStr);
  const end = parseDate(endStr);
  return Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
}
