---
type: Playbook
title: "OKF 문서 작성 절차"
description: "tasks/00-hermes/ 및 docs/ 에서 OKF 포맷 문서를 작성하는 표준 절차"
tags: [playbook, hermes, okf, workflow]
timestamp: "2026-07-29T17:30:00Z"
status: active
---

# OKF 문서 작성 절차

## 목적

Hermes Agent 가 OKF 포맷 문서를 작성할 때 따르는 표준 절차입니다. `tasks/00-hermes/` 와 `docs/` 양쪽에서 사용됩니다.

## 사전 요구사항

- [ ] 작업 대상이 `tasks/00-hermes/` 또는 `docs/` 하위 디렉토리임
- [ ] 대상 디렉토리의 `AGENTS.md` 규칙을 확인했음
- [ ] 적절한 OKF `type` 을 선택했음 (아래 테이블 참조)

## 절차

### 1단계: 타입 선택

| 기록 대상 | OKF 타입 | LLM-Wiki 카테고리 | 위치 |
|-----------|----------|-------------------|------|
| Hermes 세션 기록 | `Experiment` | Notes / Projects | `tasks/00-hermes/sessions/` |
| 컨텍스트 스냅샷 | `Ralph Context Snapshot` | Notes | `tasks/00-hermes/context-snapshots/` |
| 실행 절차 | `Playbook` | Notes | `tasks/00-hermes/playbooks/` |
| 모델 정보 | `Model` | Models | `tasks/00-hermes/models/` |
| 참고 자료 | `Reference` | Notes | `tasks/00-hermes/references/` |
| 사용법 가이드 | `Guide` | Notes | `docs/guide/` |
| 기술 참조 | `Reference` | Notes | `docs/reference/` |
| 실험 기록 | `Experiment` | Notes | `docs/notes/general-notes/` |
| 프로젝트 기록 | `Project` | Projects | `docs/notes/projects/` |

### 2단계: 파일명 결정

| 유형 | 패턴 | 예시 |
|------|------|------|
| 세션 기록 | `sessions/YYYY-MM-DD-<slug>.md` | `sessions/2026-07-29-first-hermes-session.md` |
| 컨텍스트 스냅샷 | `context-snapshots/YYYY-MM-DD-<slug>.md` | `context-snapshots/2026-07-29-initial-context.md` |
| 플레이북 | `playbooks/<name>.md` | `playbooks/okf-document-creation.md` |
| 모델 정보 | `models/<name>.md` | `models/solar-open2.md` |
| 참고 자료 | `references/<name>.md` | `references/okf-spec.md` |

### 3단계: YAML frontmatter 작성

```markdown
---
type: <선택한 OKF 타입>
title: "<문서 제목>"
description: "<한 줄 요약>"
tags: [<tag1>, <tag2>, ...]
timestamp: "<YYYY-MM-DDTHH:MM:SSZ>"
# 추가 필드 (타입에 따라):
# - session_id: "<세션 식별자>" (세션 기록)
# - status: completed|in-progress|planned (세션 기록)
# - model: "solar-open2" (세션 기록)
# - model_provider: "upstage" (세션 기록)
# - snapshot_id: "<고유 식별자>" (스냅샷)
# - related_session: "<관련 세션 파일명>" (스냅샷)
# - status: active|deprecated|archived (플레이북)
---

```

### 4단계: 본문 작성

1. `# 제목` — 문서의 주요 제목
2. 섹션별로 내용 작성 (마크다운 형식)
3. 내부 링크는 상대 경로로 작성 (`../`, `../docs/`, `../../../docs/` 등)
4. 코드 블록은 언어 지정 포함 (```python, ```bash 등)

### 5단계: 인덱스 업데이트

- `index.md` 에 새 문서 항목 추가 (해당 디렉토리의 인덱스)
- `log.md` 에 변경 기록 추가 (필요 시)
- `../../../docs/log.md` 에 주요 변경 사항 기록 (필요 시)

### 6단계: 검증

- [ ] YAML frontmatter 가 유효하고 `type` 필드가 포함되어 있음
- [ ] OKF 타입 레퍼런스에 맞는 타입을 사용함
- [ ] LLM-Wiki 카테고리가 적절함
- [ ] 상대 경로를 사용하여 내부 링크를 작성함
- [ ] `index.md` 에 새 문서 항목이 추가됨 (필요 시)
- [ ] `log.md` 에 변경 기록이 추가됨 (필요 시)

## 주의사항

- **Source 파일 불변성**: `tasks/*/source/` 디렉토리의 파일은 수정하지 않음
- **git 작업**: `git add`/`commit`/`push` 는 사용자 승인 후에만 실행
- **보호 범위**: `_private/`, `_inbox/` 파일 수정 금지
- **Schema 파일**: `AGENTS.md`, `CLAUDE.md` 는 OKF 콘텐츠 검사에서 제외
- **중복 기록 금지**: `tasks/00-hermes/` 와 `docs/` 에 같은 내용을 중복 작성하지 않음. `tasks/00-hermes/` 는 Hermes 전용 기록, `docs/` 는 프로젝트 공통 지식

## 관련 문서

- [`../index.md`](../index.md) — 루트 인덱스
- [`../log.md`](../log.md) — 변경 이력
- [`../../../docs/index.md`](../../../docs/index.md) — 프로젝트 전체 위키 인덱스
- [`../../../docs/templates/`](../../../docs/templates/) — OKF 템플릿
