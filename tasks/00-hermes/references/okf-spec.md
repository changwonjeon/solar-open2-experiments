---
type: Reference
title: "OKF Specification Reference"
description: "Open Knowledge Format (OKF) 스펙 요약 및 프로젝트에서 사용하는 타입 레퍼런스"
tags: [reference, okf, spec]
timestamp: "2026-07-29T17:30:00Z"
---

# OKF Specification Reference

## 개요

OKF(Open Knowledge Format) 는 지식 카탈로그를 위한 표준화된 마크다운 문서 포맷입니다. Google Cloud 의 knowledge-catalog 프로젝트에서 관리합니다.

- **공식 저장소**: https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf
- **포맷**: YAML frontmatter + 마크다운 본문

## OKF 문서 구조

```markdown
---
type: <Type name>              # REQUIRED
title: <Optional display name>
description: <One-line summary>
tags: [<tag>, <tag>, …]        # Optional
timestamp: <ISO 8601 datetime> # Optional
# 기타 producer-defined 키 가능
---

# 섹션 제목

본문 내용 (마크다운).
```

## 핵심 규칙

1. **YAML frontmatter 필수**: 모든 문서에 `---` 로 감싼 frontmatter 가 있어야 함
2. **`type` 필드 필수**: OKF 타입은 문서 종류를 식별하는 핵심 필드
3. **마크다운 본문**: frontmatter 이후의 본문은 표준 마크다운
4. **UTF-8 인코딩**: 모든 문서는 UTF-8 로 저장
5. **확장자**: `.md` 확장자 사용

## 프로젝트에서 사용하는 OKF 타입 레퍼런스

| 타입 | 용도 | 사용 위치 |
|------|------|----------|
| `Model` | Solar Open2 등 모델 정보 | `tasks/00-hermes/models/`, `docs/notes/models/` |
| `Paper` | 논문 요약/리뷰 | `docs/notes/papers/` |
| `Experiment` | 실험 기록, 결과 | `tasks/00-hermes/sessions/`, `docs/` |
| `Guide` | 사용법 가이드 | `docs/guide/` |
| `Playbook` | 실행 절차 | `tasks/00-hermes/playbooks/` |
| `Reference` | 레퍼런스 자료 | `tasks/00-hermes/references/`, `docs/reference/` |
| `Project` | 프로젝트 개요 | `tasks/00-hermes/sessions/`, `docs/notes/projects/` |
| `Person` | 연구자/엔지니어 | `docs/notes/people/` |
| `Dataset` | 데이터셋 설명 | `docs/` |
| `Benchmark` | 벤치마크 결과 | `docs/` |
| `Ralph Context Snapshot` | Ralph Loop 컨텍스트 동결 | `tasks/00-hermes/context-snapshots/` |
| `Work Plan` | 작업 계획 | `docs/` |
| `Execution Specification` | 실행 명세 | `docs/` |
| `Context Notes` | 컨텍스트/결정 기록 | `tasks/00-hermes/sessions/` |
| `Frozen Evaluation Contract` | 평가 계약 동결 | `docs/` |
| `Ralph Goal` | Ralph Loop 동결 목표 | `docs/` |
| `Log` | 변경 이력/기록 | `tasks/00-hermes/log.md`, `docs/log.md` |

## LLM-Wiki 카테고리 매핑

LLM-Wiki(Gptpedia) 는 OKF 와 보완적인 노트 카테고리 시스템입니다.

| LLM-Wiki 카테고리 | 설명 | OKF 타입 매핑 |
|-------------------|------|--------------|
| People | 연구자, 엔지니어링, 작가 등 인물 | `Person` |
| Models | 모델 아키텍처, 학습 방법, 파인튜닝 기법 | `Model` |
| Papers | 논문 추적, 요약, 링크 | `Paper` |
| Projects | 실험 프로젝트, 태스크 기록 | `Project` / `Experiment` |
| Notes (general-notes) | 생각, 아이디어, 로그, 템플릿 문서 | `Context Notes` / `Log` / `Reference` |
| Writing | 에세이, 블로그, 뉴스레터 | `Reference` (비 OKF) |

## 참고 링크

- OKF 공식 스펙: https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf
- LLM-Wiki (Karpathy): https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- 프로젝트 OKF 가이드: [`../../../docs/guide/okf-authoring.md`](../../../docs/guide/okf-authoring.md) (존재 시)
- 프로젝트 템플릿: [`../../../docs/templates/`](../../../docs/templates/)

## 관련 문서

- [`../index.md`](../index.md) — 루트 인덱스
- [`../log.md`](../log.md) — 변경 이력
- [`playbooks/okf-document-creation.md`](../playbooks/okf-document-creation.md) — OKF 문서 작성 절차
