# Ralphthon Experiment

## 목적
Codex CLI의 Ralph Loop를 Solar Open 2 + Claude Code로 재현하여 두 모델의 자율 실행 능력을 정량·정성 비교하는 실험입니다.

## 상태
🟡 **진행 중** — Git Checkpoint 검증 완료, 3시간 본 실행 대기 중

### 진행 상황 (2026-07-23 기준)

| 항목 | 상태 | 비고 |
|------|------|------|
| 스크립트 안정화 (9항목 보정) | ✅ 완료 | preflight.sh·commit-gate.sh 일관성 보정 + Git 히스토리 정리 |
| Blocker 7건 수정 | ✅ 완료 | 종료코드 소멸, 경로 containment, null sentinel, argv 전달, zsh 호환 등 |
| 정적 검증 (zsh -n / git diff --check) | ✅ 완료 | 전체 스크립트 정적 파싱 통과 |
| 함수 검증 (First Checkpoint) | ✅ 완료 | Gate 0~8 전체 통과 — deliverable.txt만 commit에 포함, approved_paths 정확 보존 |
| 3시간 본 실행 (Ralph Loop) | ⏳ 대기 중 | 런타임 recorder·monitor·watchdog 연결, 10분 soak/30분 rehearsal 후 실행 예정 |
| P0 완료율 / Schema 준수율 / 시간 지표 | ⏳ 미측정 | Codex 14/14(100%) vs Solar — 본 실행 후 측정 |

## 계층 구조
- `source/codex-original/`: Codex 원본 소스 (읽기 전용, 불변성 보장)
- `source/solar-adaptation/`: Solar 적응 코드 (개발 중)
- `docs/ralphthon/`: OKF Wiki 문서
- `data/`: 실험 데이터
- `output/`: 생성 산출물

## Canonical Source
- Codex 원본: `source/codex-original/`
- Solar 실행 코드: `src/scripts/ralphthon/`

## 진입점
- 실행: `src/scripts/ralphthon/start-ralph-loop.sh`
- 검증: `source/codex-original/tests/`

## 주요 산출물
- [`docs/ralphthon/RALPH_GOAL.md`](docs/ralphthon/RALPH_GOAL.md) — 랄프루프 Goal 명세 (14개 P0 항목, 10편 mock 논문)
- [`docs/ralphthon/context-notes.md`](docs/ralphthon/context-notes.md) — Track 2 준비 과정 결정과 근거
- [`docs/ralphthon/solar-vs-codex-comparison.md`](docs/ralphthon/solar-vs-codex-comparison.md) — 정성·정량 비교 분석 리포트 (본 실행 후 채움)

## 실험 개요
- **P0 항목**: 14개 (Skill 설치, 에이전트 생성, Schema 보존, Mock 10편 3회 실행, PDF 빌드 등)
- **비교 방식**: Codex 원본(100% 완료) vs Solar Open2 정성(이해도/수행력) + 과정(로그/체크포인트) + 정량(P0 완료율/schema 준수율/시간)
- **프롬프트**: `$ralph\n\n<RALPH_GOAL.md>`
- **비교 일자**: Codex 2026-07-12 vs Solar 2026-07-17 (Phase 4 실행일)