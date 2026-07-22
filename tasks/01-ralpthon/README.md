# Ralphthon Experiment

## 목적
Codex CLI의 Ralph Loop를 Solar Open 2 + Claude Code로 재현하는 실험입니다.

## 상태
진행 중

## 계층 구조
- `source/codex-original/`: Codex 원본 소스 (읽기 전용, 불변성 보장)
- `source/solar-adaptation/`: Solar 적응 코드 (개발 중)
- `docs/ralpthon/`: OKF Wiki 문서
- `data/`: 실험 데이터
- `output/`: 생성 산출물

## Canonical Source
- Codex 원본: `source/codex-original/`
- Solar 실행 코드: `src/scripts/ralpthon/`

## 진입점
- 실행: `src/scripts/ralpthon/start-ralph-loop.sh`
- 검증: `source/codex-original/tests/`
