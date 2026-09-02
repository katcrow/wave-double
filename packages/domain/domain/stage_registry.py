"""Stage 검증기 확장 지점."""

from collections.abc import Mapping
from typing import Callable
from uuid import UUID

from .run_state import Stage, validate_stage


StageVerifier = Callable[[UUID, str], bool]


def verify_candidates(run_id: UUID, stage: str) -> bool:
    """Epic 1의 candidates stage 기본 verifier."""
    return bool(run_id) and stage == Stage.CANDIDATES.value


def verify_tags(run_id: UUID, stage: str) -> bool:
    """Story 2.5의 tags stage 기본 verifier.

    실제 태깅 결과(candidate_tags 존재 여부)의 검증 권위는 ``write_stage`` RPC에 있다.
    이 기본 verifier는 candidates verifier와 동일하게 run_id/stage 유효성만 확인한다.
    """
    return bool(run_id) and stage == Stage.TAGS.value


class StageRegistry:
    def __init__(self, verifiers: Mapping[str | Stage, StageVerifier] | None = None) -> None:
        self._verifiers: dict[Stage, StageVerifier] = {
            Stage.CANDIDATES: verify_candidates,
            Stage.TAGS: verify_tags,
        }
        for stage, verifier in (verifiers or {}).items():
            self.register(stage, verifier)

    def register(self, stage: str | Stage, verifier: StageVerifier) -> None:
        self._verifiers[validate_stage(stage)] = verifier

    def verifier_for(self, stage: str | Stage) -> StageVerifier:
        try:
            return self._verifiers[validate_stage(stage)]
        except KeyError as exc:
            raise KeyError(f"no verifier registered for stage: {stage}") from exc

    def verify(self, run_id: UUID, stage: str | Stage) -> bool:
        normalized = validate_stage(stage)
        return self.verifier_for(normalized)(run_id, normalized.value)


default_registry = StageRegistry()
