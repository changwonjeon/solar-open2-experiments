---
type: Reference
title: "Hermes Task 00 LLM-Wiki 기록 가이드"
description: "Hermes 세션 기록을 LLM-Wiki 카테고리와 OKF 문서로 분류하는 로컬 참고 자료"
tags: [hermes, llm-wiki, okf, reference]
timestamp: "2026-07-29T21:46:45+09:00"
status: "active"
---

# Hermes Task 00 LLM-Wiki 기록 가이드

> 이 문서는 이 저장소의 로컬 운영 가이드입니다. 외부 표준(LLM-Wiki, OKF)의 공식 규칙을 단정하지 않으며, 이 저장소에서 실제로 사용하는 분류 방식만 설명합니다.

## 목적

이 저장소는 Hermes Agent 세션 기록을 체계적으로 축적하기 위해 두 가지 분류 체계를 함께 사용합니다:

- **OKF(Open Knowledge Format)**: 문서의 메타데이터와 콘텐츠 유형을 정의하는 포맷
- **LLM-Wiki**: 지식 베이스의 카테고리를 정의하는 분류 체계

두 체계는 서로 보완적으로 작동하지만, **서로 다른 축**입니다. OKF는 "이 문서가 무엇인가"를 정의하고, LLM-Wiki는 "이 문서를 어떤 카테고리에 넣을 것인가"를 정의합니다.

## Task 00 카테고리 매핑

| 세션 기록 대상 | OKF 타입 | LLM-Wiki 카테고리 |
|----------------|----------|-------------------|
| Sessions | `Experiment` / `Project` | `Notes (general-notes)` / `Projects` |
| Context snapshots | `Ralph Context Snapshot` | `Notes` |
| Playbooks | `Playbook` | `Notes` |
| Models | `Model` | `Models` |
| References | `Reference` | `Notes` |

**핵심**: 하나의 문서가 여러 LLM-Wiki 카테고리에 속할 수 있습니다. 예를 들어, 세션 기록은 OKF `Experiment` 이면서 LLM-Wiki `Projects` 와 `Notes` 모두에 속할 수 있습니다.

## 단일 소스 원칙

- `tasks/00-hermes/` 는 Hermes 세션 기록의 **유일한 소스**입니다.
- `docs/` 나 다른 곳에 Hermes 세션 기록을 중복 작성하지 않습니다.
- Task 00 문서는 Task 00 내에서 자체 완결성을 유지하되, 프로젝트 전체 문서와 적절히 링크합니다.

## 기존 세션 덮어쓰기 금지

- 이미 기록된 세션을 수정하지 않습니다.
- 후속 작업 내역은 별도 문서로 추가합니다.
- 기존 세션의 provenance를 변경하거나 "완료" 상태를 "미완료"로 바꾸지 않습니다.

## 상대 링크 사용

- 모든 내부 링크는 상대 경로를 사용합니다.
- `tasks/00-hermes/` 내 문서 간 링크는 `../` 를 기준으로 작성합니다.
- 루트 프로젝트 문서(`docs/`, `README.md`) 로의 링크는 `../../docs/` 또는 `../../README.md` 를 사용합니다.

## 새 문서 생성 시 색인 동기화

새 문서를 생성하면 반드시:

1. `index.md` 에 새 문서 링크를 추가합니다.
2. `log.md` 에 변경 이력을 기록합니다.
3. OKF frontmatter 의 `type` 필드가 올바른지 확인합니다.

## Provenance 원칙

이 저장소에서는 확인한 사실, 복원 정보, 추정을 명확히 구분합니다:

- **확인된 사실**: 실제 파일 존재, 실제 Git 히스토리, 실제 도구 출력에 근거한 내용
- **복원 정보**: 누락된 문서를 사후 복원한 경우 `provenance: "reconstructed-after-session"` 필드 명시
- **추정**: 근거가 불충분하여 단정할 수 없는 내용. " 추정하며" 또는 " 가능성이 있음" 으로 명시

## 관련 문서

- [`../index.md`](../index.md) — Task 00 루트 인덱스
- [`../AGENTS.md`](../AGENTS.md) — 로컬 규칙
- [`okf-spec.md`](okf-spec.md) — OKF 스펙
- [`../playbooks/okf-document-creation.md`](../playbooks/okf-document-creation.md) — OKF 문서 작성 플레이북
