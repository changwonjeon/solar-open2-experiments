---
type: Reference
title: Documentation Index
description: Root index for the _Upstage documentation bundle
---

# Documentation Index

Root index for the _Upstage documentation bundle — OKF-formatted knowledge base for Solar Open2 testing and experimentation.

## Common Wiki Directories

### Guide

Usage guides and getting-started documentation.

| 문서 | 설명 |
|------|------|
| `guide/getting-started.md` | 시작 가이드 |
| `guide/claude-code-open2.md` | Claude Code 연동 가이드 |
| `guide/hermes-agent.md` | Hermes Agent 연동 가이드 |
| `guide/okf-authoring.md` | OKF 문서 작성법 |
| `guide/troubleshooting.md` | 문제 해결 가이드 |

### Reference

Technical reference documents.

| 문서 | 설명 |
|------|------|
| `reference/solar-open2.md` | Solar Open 2 상세 스펙 |
| `reference/index.md` | 레퍼런스 인덱스 |

### Notes

LLM-Wiki style wiki notes.

| 카테고리 | 설명 |
|----------|------|
| `notes/people/` | 인물 프로필 |
| `notes/models/` | 모델 문서 |
| `notes/papers/` | 논문 요약 |
| `notes/projects/` | 프로젝트 기록 |
| `notes/writing/` | 에세이/블로그 |
| `notes/general-notes/` | 아이디어/로그/컨텍스트 |

주요 특이사항:

- [`notes/general-notes/ralphthon-spelling-correction.md`](notes/general-notes/ralphthon-spelling-correction.md) — Ralphthon 표기 오류의 확산 범위, Git 근거와 canonical 경로 정정 기록

### Templates

Document templates for OKF authoring.

| 템플릿 | 설명 |
|--------|------|
| `templates/template-model.md` | Model 문서 템플릿 |
| `templates/template-paper.md` | Paper 문서 템플릿 |
| `templates/template-experiment.md` | Experiment 문서 템플릿 |
| `templates/template-person.md` | Person 문서 템플릿 |
| `templates/template-project.md` | Project 문서 템플릿 |

## Experiment Log

- [`experiment-log.md`](experiment-log.md) — Chronological record of all experiments conducted.

## Project Log

- [`log.md`](log.md) — Migration and restructuring log for _Upstage.

## Task Wikis

### Ralph Loop Experiment (Task 01)

- [`../tasks/01-ralphthon/`](../tasks/01-ralphthon/) — Ralph Loop 재현 실험
  - Source: `../tasks/01-ralphthon/source/codex-original/` (77개 Codex 원본 파일)
  - Wiki: [`../tasks/01-ralphthon/docs/ralphthon/`](../tasks/01-ralphthon/docs/ralphthon/)
    - [`index.md`](../tasks/01-ralphthon/docs/ralphthon/index.md) — 랄프톤 실험 Wiki 인덱스
    - [`context-notes.md`](../tasks/01-ralphthon/docs/ralphthon/context-notes.md) — 작업 컨텍스트 기록
    - [`solar-vs-codex-comparison.md`](../tasks/01-ralphthon/docs/ralphthon/solar-vs-codex-comparison.md) — Solar vs Codex 비교 실험 리포트
    - [`RALPH_GOAL.md`](../tasks/01-ralphthon/docs/ralphthon/RALPH_GOAL.md) — Ralph Loop 동결 목표

### Meeting Minutes Experiment (Task 02)

- [`../tasks/02-meeting-minutes/`](../tasks/02-meeting-minutes/) — 회의록 작성 실험
  - Source: `../tasks/02-meeting-minutes/source/original/` (9개 원문)
  - Wiki: [`../tasks/02-meeting-minutes/docs/meeting-minutes/`](../tasks/02-meeting-minutes/docs/meeting-minutes/)
    - [`index.md`](../tasks/02-meeting-minutes/docs/meeting-minutes/index.md) — 회의록 실험 Wiki 인덱스
    - [`20260722-solar-open-weight-day.md`](../tasks/02-meeting-minutes/docs/meeting-minutes/20260722-solar-open-weight-day.md) — Solar Open Weight Day 행사 종합 회의록
    - [`20260722-qa-session.md`](../tasks/02-meeting-minutes/docs/meeting-minutes/20260722-qa-session.md) — 조코딩 Q&A 세션 심층 회의록

## Removed/Archived Categories

The following categories existed in previous structures but have been removed or archived:

| 이전 카테고리 | 상태 | 설명 |
|---------------|------|------|
| `model-tests/` | Removed | 구조 개편 시 제거됨 |
| `benchmarks/` | Removed | 구조 개편 시 제거됨 |
| `usage-studies/` | Removed | 구조 개편 시 제거됨 |
| `integration-tests/` | Removed | 구조 개편 시 제거됨 |
| `people/researchers/` | Removed | 구조 개편 시 제거됨 |
| `people/engineers/` | Removed | 구조 개편 시 제거됨 |
| `people/professors/` | Removed | 구조 개편 시 제거됨 |
| `people/startup-founders/` | Removed | 구조 개편 시 제거됨 |
| `people/vcs/` | Removed | 구조 개편 시 제거됨 |

> **참고**: 위 카테고리들은 2026-07-23 구조 개편 커밋(`7024b1b`)에서 `tasks/` 체계로 재편되며 제거되었습니다. 과거 경로의 문서는 현재 해당 task의 `docs/` 디렉토리에 있습니다.
