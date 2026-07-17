# Upstage Solar Open 2 테스트 작업 공간

> **Solar Open 2**는 Upstage에서 제공하는 오픈소스 대형 언어 모델입니다. 이 작업 공간은 Solar Open 2를 Claude Code, Hermes Agent와 연동하여 다양한 사용 사례를 실험하고, 그 결과를 OKF(Open Knowledge Format) 포맷으로 체계적으로 문서화하는 공간입니다.

## 🎯 프로젝트 목적

- Solar Open 2 모델의 다양한 기능 실험 및 검증
- Claude Code / Hermes Agent와의 연동 테스트
- 실험 결과, 발견사항, 인사이트를 OKF 포맷으로 축적
- LLM-Wiki 스타일의 지식 베이스 구축

## 📁 폴더 구조

```
_upstage/
├── _private/                      # 🔒 개인정보, 자격증명 (git 추적 제외)
│   ├── credentials/               # API 키, 토큰
│   ├── secrets/                   # 비밀 키, 인증서
│   └── notes/                     # 개인 메모
├── docs/                          # 📚 OKF 포맷 지식 번들
│   ├── guide/                     # 사용법 가이드
│   │   ├── getting-started.md     # 시작 가이드
│   │   ├── claude-code-open2.md   # Claude Code 연동
│   │   ├── hermes-agent.md        # Hermes Agent 연동
│   │   ├── okf-authoring.md       # OKF 문서 작성법
│   │   └── troubleshooting.md     # 문제 해결
│   ├── reference/                 # 기술 참조 문서
│   │   ├── solar-open2.md         # Solar Open 2 상세 스펙
│   │   └── index.md
│   ├── experiments/               # 실험 기록
│   │   ├── experiment-log.md      # 실험 일지
│   │   └── index.md
│   ├── notes/                     # LLM-Wiki 스타일 위키
│   │   ├── people/                # 연구자 프로필
│   │   ├── models/                # 모델 문서
│   │   ├── papers/                 # 논문 요약
│   │   ├── projects/              # 프로젝트 기록
│   │   ├── notes/                 # 아이디어/로그
│   │   └── writing/               # 에세이/블로그
│   ├── templates/                 # 문서 템플릿
│   │   ├── template-model.md
│   │   ├── template-paper.md
│   │   ├── template-experiment.md
│   │   ├── template-person.md
│   │   └── template-project.md
│   ├── index.md                   # 루트 인덱스
│   └── log.md                     # 변경 이력
├── src/                           # 💻 코드 및 스크립트
│   ├── scripts/                   # 유틸리티 스크립트
│   └── examples/                  # 예제 코드
├── data/                          # 📊 데이터
│   ├── datasets/                  # 데이터셋
│   ├── results/                   # 실험 결과
│   └── benchmarks/                # 벤치마크 결과
├── assets/                        # 🖼️ 정적 자산 (이미지 등)
├── .gitignore                     # Git 제외 설정
├── README.md                      # 이 파일
└── CLAUDE.md                      # Claude Code 운영 지침
```


## 📊 Solar Open 2 모델 정보

| 항목 | 내용 |
|------|------|
| **개발사** | Upstage (한국 스타트업) |
| **모델명** | Solar Open 2 |
| **파라미터** | ~10.7B |
| **컨텍스트** | 32K 토큰 |
| **아키텍처** | Decoder-only Transformer |
| **API 엔드포인트** | https://api.upstage.ai/v1 |
| **문서** | https://docs.upstage.ai/ |

## 🧪 Solar Open 2 비교 실험 프로젝트

### 랄프톤(Ralphthon) 재현 실험

랄프톤 해커톤(ICML 2026)에서 Codex CLI가 자율적으로 수행한 **랄프루프(Ralph Loop)**를 Solar Open 2 + Claude Code로 재현하여 두 모델의 자율 실행 능력을 비교 분석합니다.

**실험 개요:**
- **목표**: 랄프톤에서 Codex가 3시간 동안 autonomously 수행한 P0 deliverables를 Solar Open 2로 재현
- **프롬프트**: `$ralph\n\n<RALPH_GOAL.md>` (랄프톤의 Goal 파일 전체)
- **비교 방식**: 정성(이해도/수행력) + 과정(로그/체크포인트) + 정량(P0 완료율/schema 준수율/시간)

**실험 자료:** [`docs/notes/notes/ralphthon-solar-comparison.md`](docs/notes/notes/ralphthon-solar-comparison.md)

**진행 상태:** 🟡 Phase 1~3 완료 → Phase 4 실행 중 (Question Mode 전환)
---

## 🚀 실행 가이드

랄프톤 실험을 바로 실행하려면:


또는  스킬을 사용하여 에이전트가 자동으로 실행할 수 있습니다.
---

## 🗓️ Stage 1 일정

| 기간 | 내용 |
|------|------|
| **2026.07.17 ~ 07.31** | Stage 1 실험 기간 (약 2주) |
| **종료 시** | GitHub 저장소 링크 + 200자 이상 후기 제출 |

## 🔗 유용한 링크

- [Upstage Console](https://console.upstage.ai)
- [Solar Open 2 API 문서](https://console.upstage.ai/api/chat)
- [OKF 포맷 스펙](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
- [LLM-Wiki (Karpathy)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
