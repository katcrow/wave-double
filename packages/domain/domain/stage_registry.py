"""Stage 검증기 확장 지점."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from .run_state import Stage, StageStatus, validate_stage


class StageVerifier(Protocol):
    def verify(self, result: Mapping[str, object] | None = None) -> bool: ...


@dataclass(frozen=True)
class CandidatesStageVerifier:
    """후속 후보 저장 구현 전까지 stage 결과의 기본 구조만 검증한다."""

    def verify(self, result: Mapping[str, object] | None = None) -> bool:
        if result is None:
            return True
        return result.get("status", StageStatus.SUCCESS) in {
            StageStatus.SUCCESS,
            StageStatus.SUCCESS.value,
        }


class StageRegistry:
    def __init__(self, verifiers: Mapping[str | Stage, StageVerifier] | None = None) -> None:
        self._verifiers: dict[Stage, StageVerifier] = {Stage.CANDIDATES: CandidatesStageVerifier()}
        for stage, verifier in (verifiers or {}).items():
            self.register(stage, verifier)

    def register(self, stage: str | Stage, verifier: StageVerifier) -> None:
        self._verifiers[validate_stage(stage)] = verifier

    def verifier_for(self, stage: str | Stage) -> StageVerifier:
        try:
            return self._verifiers[validate_stage(stage)]
        except KeyError as exc:
            raise KeyError(f"no verifier registered for stage: {stage}") from exc

    def verify(self, stage: str | Stage, result: Mapping[str, object] | None = None) -> bool:
        return self.verifier_for(stage).verify(result)


default_registry = StageRegistry()
