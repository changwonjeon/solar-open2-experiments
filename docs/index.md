---
type: Reference
title: Experiments Index
description: Index of experimental categories and procedures for Solar Open2 testing
tags: [reference, experiments, index]
timestamp: 2026-07-22T00:00:00Z
---

# Experiments Directory

Record of experiments, tests, and research findings using Solar Open2.

## Categories

* [Ralph Loop Archive](ralpthon/index.md) - Archived Ralph Loop experiment documentation (Codex vs Solar Open2 comparison)
* [Model Tests](model-tests/index.md) - Testing model capabilities and performance
* [Benchmark Results](benchmarks/index.md) - Benchmarking results and comparisons
* [Usage Studies](usage-studies/index.md) - Real-world usage patterns and observations
* [Integration Tests](integration-tests/index.md) - Testing integrations with other tools

## Experiment Log

See [experiment-log.md](experiment-log.md) for chronological record of all experiments.

## People Analysis

분석 대상 인물 및 연구자/엔지니어 프로필

| 범주 | 설명 |
|------|------|
| [Researchers](people/researchers.md) | AI 연구자 (박사, 논문, 연구 실적 중심) |
| [Engineers](people/engineers.md) | 엔지니어 (기술 스택, 경력, 프로젝트 중심) |
| [Professors](people/professors.md) | 교수 (소속, 연구 분야, 강의, 저서 중심) |
| [Startup Founders](people/startup-founders.md) | 스타트업 창업자 (아이템, 투자, 성장 중심) |
| [VCs](people/vcs.md) | 벤처캐피탈 투자자 (포트폴리오, 투자 철학 중심) |

## Meeting Minutes

회의록 실험 (2차 실험)

### 2차 실험: 회의록 작성

회의록 작성 실험(2차 실험)은 행사 개요 문서 1건과 Tiro 노트테이킹 앱의 세션별 정리 문서 8건을 입력으로 받아, Solar Open 2(Claude Code CLI)가 이를 종합·구조화·요약하여 OKF 포맷의 회의록으로 변환하는 능력을 검증했습니다.

| 항목 | 내용 |
|------|------|
| **목표** | Solar Open2를 활용한 회의록 작성 능력 평가 |
| **동기** | 랄프톤(1차 실험) 완료 후 자연스럽게 2차 실험으로 이어짐 |
| **입력** | `_inbox/` 9개 파일 — 행사개요 txt 1건 + 세션별 정리 md 8건 (Sung Kim CEO, 이활석 CTO, 김태호 NotaAI CTO, 이태호 Upstage, Ria Upstage, 이상후 로엔컴퍼니, 김진중 Playmore, 조코딩 Q&A) |
| **출력** | `docs/experiments/meeting-minutes/20260722-solar-open-weight-day.md` — 총 8개 세션의 내용을 누락 없이 추출, 계층적으로 구조화한 OKF 포맷 회의록 |
| **상태** | `completed` |
| **수행 일시** | 2026-07-22 (수) |

## Solar Open2 Comparison

Solar Open2를 활용한 모델 비교 분석

| 비교 항목 | 설명 |
|-----------|------|
| [Model Specs](reference/solar-open2.md) | Solar Open2 모델 상세 스펙 (아키텍처, 학습, 기술, 성능, 활용) |
| [Log.md](./log.md) | 프로젝트 전반의 실험 기록 |

## Task Results

태스크별 실험 결과물 (tasks/ 디렉토리)

| 실험 | 산출물 | 설명 |
|------|--------|------|
| [Ralph Loop (01)](tasks/01-ralpthon/docs/ralpthon/index.md) | tasks/01-ralpthon/docs/ralpthon/ | 랄프톤 실험 위키 |
| [Meeting Minutes (02)](tasks/02-meeting-minutes/docs/meeting-minutes/index.md) | tasks/02-meeting-minutes/docs/meeting-minutes/ | 회의록 실험 위키 |