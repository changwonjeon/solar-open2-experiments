---
type: Reference
title: Documentation Index
description: Index of Hermes 작업 내역 기록 (OKF + LLM-Wiki style)
tags: [hermes, okf, wiki, log]
timestamp: "2026-07-29T17:30:00Z"
---

# Hermes 작업 내역 인덱스

이 디렉토리는 Hermes Agent 세션의 작업 내역을 OKF frontmatter + LLM-Wiki 카테고리 스타일로 기록합니다.

## 디렉토리 구조

```
tasks/00-hermes/
├── index.md                  # 이 파일 — 루트 인덱스
├── log.md                    # 변경 이력 / 세션별 로그 인덱스
├── sessions/                 # 세션별 기록 (LLM-Wiki: Notes / Projects)
│   ├── 2026-07-29-first-hermes-session.md
│   └── ...
├── context-snapshots/        # 컨텍스트 동결 스냅샷 (OKF: Ralph Context Snapshot)
│   └── 2026-07-29-initial-context.md
├── playbooks/                # 실행 절차 / 작업 플레이북 (OKF: Playbook)
│   └── ...
├── references/               # 참고 자료 (OKF Reference)
│   └── llm-wiki-guide.md
└── AGENTS.md                 # 이 디렉토리 로컬 규칙 (Schema)
```

## OKF 타입 매핑

| Hermes 기록 대상 | OKF 타입 | LLM-Wiki 카테고리 |
|-----------------|----------|-------------------|
| 세션별 작업 기록 | `Experiment` / `Project` | `Notes (general-notes)` / `Projects` |
| 컨텍스트 스냅샷 | `Ralph Context Snapshot` | `Notes` |
| 실행 절차/워크플로우 | `Playbook` | `Notes` |
| 모델/환경 정보 | `Model` | `Models` |
| 변경 이력 | `Log` | `Notes` |
| 참고 자료 | `Reference` | `Notes` |

## 기록 규칙

1. **세션 종료 시 기록 생성**: 각 Hermes 세션이 끝날 때 `sessions/` 에 해당 세션의 작업 내역을 OKF 포맷으로 기록
2. **작업 발생 시 즉시 로그**: 중요한 결정/변경은 `log.md` 에 즉시 기록
3. **컨텍스트 스냅샷**: 복잡한 작업 전/후에 `context-snapshots/` 에 상태 동결
4. **플레이북**: 반복 작업은 `playbooks/` 에 절차 문서화
5. **루트 log.md 업데이트**: `../../docs/log.md` 에도 주요 변경 사항 기록 (선택)

## 관련 문서

- [`../../docs/index.md`](../../docs/index.md) — 프로젝트 전체 위키 인덱스
- [`../../docs/notes/general-notes/`](../../docs/notes/general-notes/) — 프로젝트 일반 노트
- [`../`](../) — 실험 태스크 (01-ralphthon, 02-meeting-minutes, ...)
- [`context-snapshots/2026-07-29-initial-context.md`](context-snapshots/2026-07-29-initial-context.md) — 초기 컨텍스트 스냅샷 (사후 복원)
- [`references/llm-wiki-guide.md`](references/llm-wiki-guide.md) — LLM-Wiki 가이드
