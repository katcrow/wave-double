const KST_TIME_FORMATTER = new Intl.DateTimeFormat("ko-KR", {
  timeZone: "Asia/Seoul",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

const KST_DATETIME_FORMATTER = new Intl.DateTimeFormat("ko-KR", {
  timeZone: "Asia/Seoul",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

export function formatKstTime(iso: string): string {
  return KST_TIME_FORMATTER.format(new Date(iso));
}

export function formatKstDateTime(iso: string): string {
  return KST_DATETIME_FORMATTER.format(new Date(iso));
}

/** Design Notes: published_at(없으면 finished_at ?? started_at) 기준 경과 60분 이상이면 stale. */
export function isStaleSince(iso: string, thresholdMinutes = 60): boolean {
  const elapsedMs = Date.now() - new Date(iso).getTime();
  return elapsedMs >= thresholdMinutes * 60 * 1000;
}
