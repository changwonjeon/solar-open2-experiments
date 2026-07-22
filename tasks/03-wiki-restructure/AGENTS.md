# Wiki 구조 재편 작업 에이전트 실행 규칙

이 문서는 `tasks/03-wiki-restructure/` 작업에 참여하는 에이전트가 따르는 실행 규칙입니다.

## 계층별 원칙

### Source 계층
- **경로**: `tasks/01-ralpthon/source/codex-original/`
- **원칙**: **읽기 전용 — 내용 수정 금지**
- 원본 복구 시 반드시 `git hash-object`로 blob ID 일치 확인

### Wiki 계층
- **경로**: `docs/`
- **원칙**: **OKF 포맷 준수 필수 — `type` frontmatter 필수**
- 모든 위키 문서는 OKF frontmatter를 포함해야 함

### Output 계층
- **경로**: `tasks/03-wiki-restructure/`
- **원칙**: **생성 산출물 — 소스 변경 금지**
- 이 디렉토리의 파일은 결과물을 기록하며, 원본 소스 데이터를 포함하지 않음

### Schema 계층
- **경로**: `AGENTS.md`, `CLAUDE.md`
- **원칙**: **`@AGENTS.md` 한 줄 참조**
- 이 계층은 위키 구조/워크플로우 규칙을 정의

## 보호 대상

다음 항목은 **절대 수정하지 않음**:

1. `tasks/02-meeting-minutes/` — 원본 9개 파일, 회의록, LinkedIn 산출물
2. `_private/` — 개인정보, 자격증명 (gitignore 됨)
3. `_inbox/` — 전달용 폴더
4. `src/data/results/` — 결과 데이터
5. `.gitignore` 처리된 모든 파일

## 실행 제약

- **대량 이동/삭제 시**: 사용자 승인 필수
- **git add/commit/push**: 사용자 승인 후에만 실행
- **각 단계 종료 시**: 검증 게이트 통과 확인 필수 (100% 보존율)

## 검증 게이트

| Gate | 단계 | 통과 기준 |
|------|------|-----------|
| G1 | Step 2 | 원본 blob 보존 100% |
| G2 | Step 2 | HEAD 삭제 자산 보존 100% |
| G3 | Step 3 | canonical 중복 0 |
| G4 | Step 4 | OKF 위반 0 |
| G5 | Step 5 | 모든 gate 종합 PASS |

## 중단 조건

- 원본 blob 보존율이 100%가 아니면 다음 단계로 진행하지 않음
- `tasks/02-meeting-minutes/` 보호 자료의 hash가 예상과 다르면 즉시 중단

## 작업 기록

각 단계 종료 시 `work-log.md`에 진행 상황을 기록하십시오.
