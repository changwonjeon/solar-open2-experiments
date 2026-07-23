# Ralph Loop — Codex 원본 실험 프로젝트

랄프톤 해커톤(ICML 2026)에서 Codex CLI가 수행한 랄프루프(Ralph Loop) 원본 자료 보관용 디렉토리.

## 보관 내용

- `checklist.md` — OKF 전환 체크리스트 (Codex-era)
- `execution-log.md` — 실행 로그 (Codex-era)
- `.codex/` — Codex 에이전트 스킬 및 설정 파일 (원본)
  - `skills/auto-research/` — 공식 auto-research Skill
  - `skills/ralphthon-track2-review-agent/` — Track 2 Review Agent Skill
  - `agents/` — Review Worker, Verifier, Auditor 에이전트 설정
- `fixtures/` — Mock 논문 픽스처
  - `throughput/paper-001~010.md` — 처리량 테스트용 10편
  - `quality/EVALUATION_CONTRACT.md` — 품질 평가 계약

## 참고

이 디렉토리의 자료는 Codex CLI 기준으로 작성된 원본이며, Solar Open 2 + Claude Code 재현 실험에서의 분석·비교 자료는 `docs/experiments/ralphthon/`에 별도로 보관된다.
