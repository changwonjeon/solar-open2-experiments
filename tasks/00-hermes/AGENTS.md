# Hermes 작업 내역 — 로컬 에이전트 규칙

이 디렉토리는 Hermes Agent 세션의 작업 내역을 OKF frontmatter + LLM-Wiki 스타일 마크다운으로 기록하는 곳입니다.

## 핵심 원칙

1. **단일 소스 오브 트루스**: `tasks/00-hermes/` 는 Hermes 세션 기록의 유일한 저장소입니다. `docs/` 나 다른 곳에 중복 기록하지 않습니다.
2. **OKF frontmatter 필수**: 모든 `.md` 파일에 `type` 필드를 포함한 YAML frontmatter를 작성합니다.
3. **LLM-Wiki 카테고리 분류**: Notes, Projects, Models 등의 카테고리로 문서를 분류합니다.
4. **세션 기반 기록**: 각 세션은 `sessions/YYYY-MM-DD-<slug>.md` 형식의 독립 문서로 기록됩니다.
5. **보호 범위**:
   - `sessions/` 의 기존 파일 내용을 임의로 수정하지 않습니다.
   - 이미 기록된 세션을 덮어쓰지 않고, 후속 작업 내역을 별도 문서로 추가합니다.
   - `git add`/`commit`/`push` 는 사용자 승인 후에만 실행합니다.

## 기록 시점

| 시점 | 기록 대상 | 파일 위치 |
|------|----------|----------|
| 세션 시작 | 세션 컨텍스트, 목표, 환경 | `sessions/YYYY-MM-DD-<slug>.md` 생성 |
| 작업 중간 | 주요 결정, 컨텍스트 변경 | `context-snapshots/` 스냅샷 + 로그 코멘트 |
| 세션 종료 | 전체 작업 요약, 결과, 배운 점 | `sessions/YYYY-MM-DD-<slug>.md` 최종화 |
| 중요 변경 | 구조 변경, 규칙 수정 | `log.md` + `index.md` 업데이트 |

## 디렉토리 구조

```
tasks/00-hermes/
├── index.md                  # 루트 인덱스 (이 디렉토리 개요)
├── log.md                    # 변경 이력 색인
├── sessions/                 # 세션별 기록 (OKF: Experiment/Project, LLM-Wiki: Notes/Projects)
├── context-snapshots/        # 컨텍스트 동결 스냅샷 (OKF: Ralph Context Snapshot)
├── playbooks/                # 실행 절차 (OKF: Playbook)
├── models/                   # 모델/환경 정보 (OKF: Model, LLM-Wiki: Models)
├── references/               # 참고 자료 (OKF: Reference)
└── AGENTS.md                 # 이 파일 — 로컬 규칙 (Schema)
```

## 문서 작성 템플릿

### 세션 기록 (sessions/)

```markdown
---
type: Experiment
title: "<세션명>"
description: "<한 줄 요약>"
tags: [hermes, session, okf]
timestamp: "<YYYY-MM-DDTHH:MM:SSZ>"
session_id: "<세션 식별자>"
status: completed|in-progress|planned
model: "solar-open2"
model_provider: "upstage"
---

# 세션 개요

- **일시**: <세션 일시>
- **목표**: <세션 목표>
- **작업 디렉토리**: <작업한 경로>

# 작업 내역

## <단계 1>

- **작업**: <작업 설명>
- **도구**: <사용한 도구>
- **결과**: <결과 요약>
- **소요 시간**: <예상/실측>

## <단계 2>

...

# 결과 및 산출물

- **생성 파일**: <생성된 파일 목록>
- **변경 사항**: <변경된 파일 요약>
- **생성된 문서**: <작성된 위키 문서>

# 배운 점 / 개선 사항

- <배운 점>
- <다음에 개선할 점>

# 관련 문서

- [`../../../docs/index.md`](../../../docs/index.md)
- [`../log.md`](../log.md)
```

### 컨텍스트 스냅샷 (context-snapshots/)

```markdown
---
type: Ralph Context Snapshot
title: "<스냅샷명>"
description: "<컨텍스트 동결 목적>"
tags: [context, snapshot, hermes]
timestamp: "<YYYY-MM-DDTHH:MM:SSZ>"
snapshot_id: "<고유 식별자>"
related_session: "<관련 세션 파일명>"
---

# 컨텍스트 스냅샷

## 환경

- **작업 디렉토리**: <경로>
- **Git 브랜치**: <브랜치명>
- **Git 상태**: <상태 요약>
- **활성 가상 환경**: <가상환경 정보>

## 활성 컨텍스트

- **현재 작업**: <진행 중인 작업>
- **관련 파일**: <작업 중인 파일 목록>
- **결정 사항**: <이미 결정한 사항>
- **보류 중인 결정**: <미결정 사항>

## 메모

- <추가 메모>
```

### 플레이북 (playbooks/)

```markdown
---
type: Playbook
title: "<플레이북명>"
description: "<실행 절차 요약>"
tags: [playbook, hermes, workflow]
timestamp: "<YYYY-MM-DDTHH:MM:SSZ>"
status: active|deprecated|archived
---

# <플레이북명>

## 목적

<플레이북의 목적과 사용 시점>

## 사전 요구사항

- <필요 조건 1>
- <필요 조건 2>

## 절차

1. <단계 1>
2. <단계 2>
...

## 검증

- [ ] <검증 항목 1>
- [ ] <검증 항목 2>

## 관련 문서

- [`../index.md`](../index.md)
```

## 파일 명명 규칙

| 유형 | 패턴 | 예시 |
|------|------|------|
| 세션 기록 | `sessions/YYYY-MM-DD-<slug>.md` | `sessions/2026-07-29-first-hermes-session.md` |
| 컨텍스트 스냅샷 | `context-snapshots/YYYY-MM-DD-<slug>.md` | `context-snapshots/2026-07-29-initial-context.md` |
| 플레이북 | `playbooks/<name>.md` | `playbooks/okf-document-creation.md` |
| 모델 정보 | `models/<name>.md` | `models/solar-open2.md` |
| 참고 자료 | `references/<name>.md` | `references/okf-spec.md` |

## 검증 체크리스트

문서 작성 후 다음을 확인합니다:

- [ ] YAML frontmatter 가 유효하고 `type` 필드가 포함되어 있음
- [ ] OKF 타입 레퍼런스에 맞는 타입을 사용함
- [ ] LLM-Wiki 카테고리가 적절함
- [ ] 상대 경로를 사용하여 내부 링크를 작성함
- [ ] `index.md` 에 새 문서 항목이 추가됨 (필요 시)
- [ ] `log.md` 에 변경 기록이 추가됨 (필요 시)
