---
type: Project
title: Ralphthon 철자 인식 오류 재현 실험
description: Solar Open 2에서 Ralphthon 철자 보존·추론·교정 및 저장소 확산을 재현하는 실험
tags: [solar-open2, claude-code, ralphthon, spelling, evaluation, task-05]
timestamp: 2026-07-23T15:26:14Z
---

# Ralphthon 철자 인식 오류 재현 실험 — Wiki 인덱스

## 개요

이 실험은 Solar Open 2 모델이 `Ralphthon`이라는 철자를 어떻게 인식하고 보존하는지, 그리고 저장소 환경에서 철자 오류가 어떻게 확산되는지를 체계적으로 재현하기 위해 설계되었습니다.

## 실험 구성

### 실험 A — 철자 인식과 보존 (6조건 × 10회 = 60 probe)

| Case | 조건 | 판정 기준 |
|------|------|-----------|
| A1 | 명시적 복사 | exact match |
| A2 | 음차 추론 | 생성 철자 분포 (오류 판정 금지) |
| A3 | 조어 구성 | Ralphthon 도출 여부 |
| A4 | 오타 교정 | 교정 준수율 |
| A5 | 충돌 문맥 | glossary 준수율 |
| A6 | 지연 유지 | 최종 보존율 |

### 실험 B — 저장소 오류 확산 (10 trial)

| 측정 항목 | 설명 |
|-----------|------|
| 신규 오류 생성 | Solar Open 2가 잘못된 철자를 새로 생성했는지 |
| 확산 범위 | 오타가 확산된 파일과 경로 수 |
| 확산 표면 | 파일명, 폴더명, 본문, 코드 식별자 |
| glossary 준수 | authoritative glossary 준수 여부 |
| 잔존/재발 | 명시적 교정 뒤 잔존 오타와 재발 여부 |

## 관련 자료

- [실행 명세](../../EXECUTION_PLAN.md) — 실험의 전체 실행 명세
- [실험 결과](results.md) — 조건별 결과와 통계
- [상위 Task 01](../01-ralphthon/docs/ralphthon/) — 랄프루프 실험 결과
- [상위 README](../../README.md) — 프로젝트 개요

## 보호 범위

- 기존 `tasks/01-ralphthon/` ~ `tasks/04-tokenizer-comparison/` 수정 금지
- `_private/`, `_inbox/`, 기존 result/ignored 파일 수정 금지
- `git add`/`commit`/`push`는 사용자 승인 필요
