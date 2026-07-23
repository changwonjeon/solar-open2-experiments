# Meeting Minutes Experiment

## 목적
Solar Open 2(Claude Code CLI)를 활용하여 회의록 자동 작성 및 품질 평가 실험입니다. 행사 개요 문서 1건과 Tiro 노트테이킹 앱의 세션별 정리 문서 8건을 입력으로 받아, 이를 종합·구조화·요약하여 OKF 포맷의 회의록으로 변환하는 능력을 검증합니다.

## 상태
🟢 **완료** — 종합 회의록 + Q&A 세션 회의록 생성 완료. 품질 4차원(정보추출·구조화·정확성·OKF 준수) 모두 양호.

### 진행 상황 (2026-07-23 기준)

| 항목 | 상태 | 비고 |
|------|------|------|
| 종합 회의록 작성 | ✅ 완료 | 8개 세션 종합 — 행사 개요, 진행 일정, 세션별 상세 요약, 결정사항/액션아이템 10건, 종합 인사이트 포함 |
| Q&A 세션 회의록 작성 | ✅ 완료 | 조코딩 Q&A 세션 심층 회의록 (패널 토론 집중 기록) |
| 정보 추출 품질 | ✅ 양호 | 9개 파일 전체 핵심 내용 누락 없이 포착 (모델 아키텍처 4요소, NotaAI 3기술, 활용사례 4건, Q&A 11개 주제) |
| 구조화 품질 | ✅ 양호 | 시간순 세션 → 주제별 분류 → 행동항목 테이블 → 인사이트 종합의 다층적 계층 구조 |
| 정확성 | ✅ 양호 | 수치(250B, 1M, GPU 2장, 35,000명, 80% 성능저하 등) 원문 유지. 발표자명·직함 정확도 확인 |
| OKF 준수 | ✅ 양호 | `type: Experiment`, `tags`, `timestamp`, `input_sources` frontmatter 완전 준수 |

## 계층 구조
- `source/original/`: 회의록 원본 (읽기 전용, 불변성 보장)
- `docs/meeting-minutes/`: OKF Wiki 문서
- `data/`: 실험 데이터
- `output/`: 생성 산출물 (LinkedIn 포스트 포함)

## Canonical Source
- 회의록 원본: `source/original/`

## 진입점
- 원본: `source/original/`
- Wiki: `docs/meeting-minutes/`
- 산출물: `output/`

## 주요 산출물
- [`docs/meeting-minutes/20260722-solar-open-weight-day.md`](docs/meeting-minutes/20260722-solar-open-weight-day.md) — Solar Open Weight Day 행사 종합 회의록 (25KB, 8개 세션)
- [`docs/meeting-minutes/20260722-qa-session.md`](docs/meeting-minutes/20260722-qa-session.md) — 조코딩 Q&A 세션 심층 회의록

## 입력 자료
- **행사개요**: txt 1건 — Solar Open Weight Day 행사 개요
- **세션별 정리**: md 8건
  - Sung Kim CEO — Solar Open2 모델 아키텍처(MoE), 250B/15B active/1M context/196K vocab/NoPE
  - 이활석 CTO — Solar 성능 평가(MMLU 78.7%, HaluEval 81.3%, 한국어 특화)
  - 김태호 NotaAI CTO — Edge AI 모델 경량화(프루닝, 양자화, 지식증류)
  - 이태호 Upstage — Solar API 서비스(업스테이지 콘솔, 배치/스트리밍 API, 함수 호출)
  - Ria Upstage — Solar 파인튜닝 파이프라인(LoRA/QLoRA, 학습 데이터 구성)
  - 이상후 로엔컴퍼니 — Melon 음악 추천 시스템과 AI 활용 사례
  - 김진중 Playmore — 게임 AI NPC, 강화학습, 실시간 추론 최적화
  - 조코딩 Q&A — 모델 선택 가이드, GPU 2장 파인튜닝, 오픈소스 vs API, 한국어 성능, 커뮤니티 생태계

## 다음 단계
- 실험 개요 문서 작성 (`experiment-overview.md`)
- 품질 평가 지표 체계화