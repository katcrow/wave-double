"""배치 실행 계보의 순수 상태 규칙.

이 모듈은 Supabase, SQL, HTTP를 알지 않는다. 영속 상태의 최종 권위는
마이그레이션에 정의된 RPC에 있으며, 이 모듈은 호출자가 잘못된 키와 전이를
만들지 않도록 동일한 어휘를 제공한다.
"""

from dataclasses import dataclass
from datetime import date, datetime, time
from enum import StrEnum
import re


class BatchKind(StrEnum):
    PREMARKET = "premarket"
    INTRADAY = "intraday"
    CLOSE = "close"


class Trigger(StrEnum):
    SCHEDULE = "schedule"
    MANUAL = "manual"


class RunStatus(StrEnum):
    RUNNING = "running"
    READY_TO_PUBLISH = "ready_to_publish"
    PUBLISHED = "published"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"
    SUPERSEDED = "superseded"
    CANCELLED = "cancelled"


class Stage(StrEnum):
    CANDIDATES = "candidates"
    TAGS = "tags"
    SUPPLY_3DAY = "supply_3day"
    MARKET_SUPPLY = "market_supply"
    OUTCOME_TRACKING = "outcome_tracking"
    BIAS = "bias"


class StageStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


STAGES: tuple[Stage, ...] = tuple(Stage)
REQUIRED_STAGES: tuple[Stage, ...] = (
    Stage.CANDIDATES,
    Stage.TAGS,
    Stage.SUPPLY_3DAY,
    Stage.MARKET_SUPPLY,
)
_SLOT_RE = re.compile(r"^(?:[01]\d|2[0-3]):(?:00|20|30|40)$")


@dataclass(frozen=True)
class LogicalRunKey:
    trading_day: date
    batch_kind: BatchKind
    slot: time | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.batch_kind, BatchKind):
            object.__setattr__(self, "batch_kind", BatchKind(self.batch_kind))
        if self.batch_kind is BatchKind.INTRADAY and self.slot is None:
            raise ValueError("intraday logical keys require a KST slot")
        if self.batch_kind is not BatchKind.INTRADAY and self.slot is not None:
            raise ValueError("only intraday logical keys may have a slot")
        if self.slot and (
            self.slot.second or self.slot.microsecond or self.slot.minute not in (0, 20, 30, 40)
        ):
            # 2026-09-16부터 신규 슬롯은 :30(60분 간격, Neo 확인)이며, :00/:20/:40은
            # 이전 20분 간격 스케줄의 과거 이력(logical_runs 등)과의 호환을 위해 남긴다.
            raise ValueError("intraday slot must be a KST :00/:20/:30/:40 boundary")

    @property
    def value(self) -> str:
        if self.slot is None:
            return f"{self.batch_kind.value}:{self.trading_day.isoformat()}"
        return f"{self.batch_kind.value}:{self.trading_day.isoformat()}:{self.slot:%H:%M}"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def parse(cls, value: str) -> "LogicalRunKey":
        parts = value.split(":", 2)
        if len(parts) not in (2, 3):
            raise ValueError("invalid logical run key")
        try:
            kind = BatchKind(parts[0])
            day = date.fromisoformat(parts[1])
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid logical run key") from exc
        if len(parts) == 2:
            return cls(day, kind)
        if kind is not BatchKind.INTRADAY or not _SLOT_RE.fullmatch(parts[2]):
            raise ValueError("intraday logical key requires an HH:MM KST slot")
        hour, minute = map(int, parts[2].split(":"))
        return cls(day, kind, time(hour, minute))


def initial_stage_status() -> dict[str, StageStatus]:
    return {stage.value: StageStatus.PENDING for stage in STAGES}


def validate_stage(stage: str | Stage) -> Stage:
    try:
        return stage if isinstance(stage, Stage) else Stage(stage)
    except ValueError as exc:
        raise ValueError(f"unknown stage: {stage}") from exc


def validate_stage_transition(
    current: str | StageStatus, target: str | StageStatus
) -> StageStatus:
    current_status = current if isinstance(current, StageStatus) else StageStatus(current)
    target_status = target if isinstance(target, StageStatus) else StageStatus(target)
    allowed = {
        StageStatus.PENDING: {StageStatus.RUNNING},
        StageStatus.RUNNING: {
            StageStatus.SUCCESS,
            StageStatus.FAILED,
            StageStatus.PARTIAL,
        },
    }
    if target_status is current_status and current_status in {
        StageStatus.SUCCESS,
        StageStatus.FAILED,
        StageStatus.PARTIAL,
    }:
        return target_status
    if target_status not in allowed.get(current_status, set()):
        raise ValueError(f"invalid stage transition: {current_status} -> {target_status}")
    return target_status


def can_publish(stage_status: dict[str, str | StageStatus]) -> bool:
    return all(stage_status.get(stage.value) == StageStatus.SUCCESS for stage in REQUIRED_STAGES)
