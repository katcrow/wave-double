# Supabase Migrations

이 디렉터리는 wave-double의 Supabase Postgres 스키마 변경을 관리한다.

## 명명 규약 (AD-14)

각 마이그레이션 파일은 단일 timestamp 접두어를 가진 SQL 파일이다:

```
YYYYMMDDHHMM_description.sql
```

- `YYYYMMDDHHMM` — 4자리 연도, 2자리 월, 2자리 일, 2자리 시, 2자리 분의 **UTC 기준** timestamp (예: `202609011400_create_candidates.sql`)
- `description` — snake_case의 짧은 설명
- 확장자는 반드시 `.sql`

## 규칙

- Supabase CLI가 이 timestamp 순서대로 마이그레이션을 적용한다. 항상 **forward-only**로 진화한다(AD-14 expand-migrate-contract).
- 한 파일이 하나의 원자적 변경을 표현한다. schema, RLS policy, view, RPC도 모두 이 경로로만 변경한다(AD-14).
- 운영 Supabase 작업은 루트 `AGENTS.md` 정책에 따라 supabase MCP로 운영 프로젝트(`qqhjeumlecaudsiqhhdu`)에 적용한다. 배치 실행 경로는 `.github/workflows/scheduled-batch.yml`을 따른다.
- 운영 rollback은 destructive down migration이 아니라 앱 rollback + forward-fix로 처리한다(AD-14).
- 데이터 복구는 검증된 backup만 사용한다(AD-17).

## 현재 상태

스키마·RLS·RPC 변경 이력은 이 디렉터리의 SQL 파일로 관리한다.
