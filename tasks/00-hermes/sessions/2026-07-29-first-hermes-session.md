---
type: Experiment
title: "Hermes 작업 내역 기록 시스템 구축 (첫 세션)"
description: "tasks/00-hermes/ 디렉토리 구조 생성 및 OKF+LLM-Wiki 스타일 기록 체계 구축"
tags: [hermes, session, okf, wiki, setup]
timestamp: "2026-07-29T17:29:00Z"
session_id: "2026-07-29-001"
status: completed
model: "solar-open2"
model_provider: "upstage"
---

# 세션 개요

- **일시**: 2026-07-29
- **목표**: Hermes Agent 작업 내역을 `tasks/00-hermes/` 에 OKF frontmatter + LLM-Wiki 스타일로 기록하는 시스템 구축
- **작업 디렉토리**: `/home/redux80/_Upstage`

# 작업 내역

## 단계 1: 기존 구조 파악

- `tasks/` 디렉토리 내 01~06 실험 태스크 확인 (ralphthon, meeting-minutes, wiki-restructure, tokenizer-comparison, ralphthon-spelling-evaluation, practice-aaws)
- `docs/` 의 OKF 포맷 구조 확인 (guide/, reference/, notes/, templates/, experiment-log.md, log.md, index.md)
- `docs/AGENTS.md` 에서 위키 에이전트 규칙 확인
- `tasks/01-ralphthon/AGENTS.md` 에서 태스크 로컬 규칙 확인
- OKF 타입 레퍼런스 및 LLM-Wiki 카테고리 참고

## 단계 2: 디렉토리 구조 설계

```
tasks/00-hermes/
├── index.md                  # 루트 인덱스
├── log.md                    # 변경 이력 / 세션별 로그 인덱스
├── sessions/                 # 세션별 기록 (OKF: Experiment/Project)
├── context-snapshots/        # 컨텍스트 동결 스냅샷 (OKF: Ralph Context Snapshot)
├── playbooks/                # 실행 절차 (OKF: Playbook)
├── models/                   # 모델/환경 정보 (OKF: Model)
├── references/               # 참고 자료 (OKF: Reference)
└── AGENTS.md                 # 로컬 규칙 (Schema)
```

OKF 타입 매핑 설계:
- 세션별 작업 기록 → `Experiment` / `Project` (LLM-Wiki: Notes / Projects)
- 컨텍스트 스냅샷 → `Ralph Context Snapshot` (LLM-Wiki: Notes)
- 실행 절차/워크플로우 → `Playbook` (LLM-Wiki: Notes)
- 모델/환경 정보 → `Model` (LLM-Wiki: Models)
- 변경 이력 → `Log` (LLM-Wiki: Notes)
- 참고 자료 → `Reference` (LLM-Wiki: Notes)

## 단계 3: 파일 생성 (초기)

- `tasks/00-hermes/index.md` — 루트 인덱스 (2,302 bytes, 52 lines)
- `tasks/00-hermes/AGENTS.md` — 로컬 규칙 (5,443 bytes, 184 lines)
- `tasks/00-hermes/log.md` — 변경 이력 색인 (1,739 bytes, 49 lines)
- `tasks/00-hermes/sessions/` — 빈 디렉토리
- `tasks/00-hermes/context-snapshots/` — 빈 디렉토리
- `tasks/00-hermes/playbooks/` — 빈 디렉토리
- `tasks/00-hermes/models/` — 빈 디렉토리
- `tasks/00-hermes/references/` — 빈 디렉토리

## 단계 4: 경로 정정 (폴더명 오타 수정)

- **문제**: `task/00-hermes/` 로 생성되었으나 프로젝트 구조가 `tasks/` 체계임
- **조치**: `mv task/00-hermes/ tasks/00-hermes/` 실행
- **발견된 이슈**: `mv` 가 `tasks/00-hermes/00-hermes/` 중첩 구조를 생성
- **해결**: `mv tasks/00-hermes/00-hermes/* tasks/00-hermes/` 후 `rmdir` 로 중첩 디렉토리 제거
- **상대 경로 일괄 수정**:
  - `index.md`: `../../docs/` → `../../../docs/`, `../` → `../`
  - `log.md`: `task/00-hermes/` → `tasks/00-hermes/`, `../../docs/` → `../../../docs/`
  - `AGENTS.md`: 템플릿 내 상대 경로 `../` → `../` ( sessions/, context-snapshots/, playbooks/ 는 동일 depth 이므로 변경 없음)

## 단계 5: 현재 세션 기록 작성

- `sessions/2026-07-29-first-hermes-session.md` 생성 (현재 파일)
- `log.md` 의 세션 색인에 항목 추가
- `log.md` 의 변경 이력에 경로 정정 기록 추가

# 결과 및 산출물

## 생성 파일

| 파일 | 크기 | 용도 |
|------|------|------|
| `tasks/00-hermes/index.md` | 2,312 bytes | 루트 인덱스 |
| `tasks/00-hermes/AGENTS.md` | 5,454 bytes | 로컬 에이전트 규칙 |
| `tasks/00-hermes/log.md` | 1,858 bytes | 변경 이력 색인 |
| `sessions/2026-07-29-first-hermes-session.md` | (이 파일) | 첫 세션 기록 |

## 디렉토리 구조

```
tasks/00-hermes/                         44 files (dirs + md)
├── AGENTS.md                            184 lines
├── index.md                             52 lines
├── log.md                               50 lines
├── sessions/                            (empty)
├── context-snapshots/                   (empty)
├── playbooks/                           (empty)
├── models/                              (empty)
└── references/                          (empty)
```

# 배운 점 / 개선 사항

- `mv` 명령은 소스 디렉토리가 존재할 때 타겟 디렉토리 안으로 내용을 이동시키므로, 이미 `tasks/00-hermes/` 가 존재하면 중첩 구조가 생성됨. `mv src/* dest/` 패턴으로 명시적 이동이 필요
- OKF + LLM-Wiki 조합은 프로젝트의 기존 문서 스타일과 자연스럽게 통합됨
- 상대 경로 참조는 디렉토리 깊이 변경 시 일괄 수정이 필요함. 초기 설계 시 깊이 계산을 정확히 하는 것이 중요

# 관련 문서

- [`../index.md`](../index.md) — 루트 인덱스
- [`../log.md`](../log.md) — 변경 이력
- [`../../../docs/index.md`](../../../docs/index.md) — 프로젝트 전체 위키 인덱스
- [`../../../docs/notes/general-notes/`](../../../docs/notes/general-notes/) — 프로젝트 일반 노트
