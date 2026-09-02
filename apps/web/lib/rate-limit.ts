/**
 * Story 1.10 (AD-7): `/api/dispatch`의 사용자별 rate limit.
 * 새 의존성을 추가하지 않는다는 스펙 제약에 따라 in-memory sliding window로 구현한다.
 * 단일 운영자 전제(Never 절) 하에서는 서버리스 다중 인스턴스 우회가 트레이드오프로 이미 수용됐다
 * (spec Review Triage Log 기각 사유 참고). 프로세스 재시작 시 카운터는 초기화된다.
 */
export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  retryAfterMs: number;
}

export class RateLimiter {
  private readonly hits = new Map<string, number[]>();
  private readonly limit: number;
  private readonly windowMs: number;

  constructor(limit: number, windowMs: number) {
    if (limit <= 0) throw new Error("limit must be positive");
    if (windowMs <= 0) throw new Error("windowMs must be positive");
    this.limit = limit;
    this.windowMs = windowMs;
  }

  check(key: string, now: number = Date.now()): RateLimitResult {
    const windowStart = now - this.windowMs;
    const existing = this.hits.get(key) ?? [];
    const recent = existing.filter((timestamp) => timestamp > windowStart);

    if (recent.length >= this.limit) {
      const oldest = recent[0];
      this.hits.set(key, recent);
      return { allowed: false, remaining: 0, retryAfterMs: Math.max(0, oldest + this.windowMs - now) };
    }

    recent.push(now);
    this.hits.set(key, recent);
    return { allowed: true, remaining: this.limit - recent.length, retryAfterMs: 0 };
  }
}
