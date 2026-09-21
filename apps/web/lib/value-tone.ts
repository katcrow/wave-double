export type ValueTone = "up" | "down" | "neutral";

/** 국내 주식시장 관례: 양수(상승)는 빨강, 음수(하락)는 파랑으로 표시한다. */
export function toneFromSign(value: number | null | undefined): ValueTone {
  if (value === null || value === undefined || !Number.isFinite(value)) return "neutral";
  if (value > 0) return "up";
  if (value < 0) return "down";
  return "neutral";
}

export function toneClassName(tone: ValueTone): string | undefined {
  return tone === "neutral" ? undefined : `value-tone--${tone}`;
}
