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

## 🚀 시작하기

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install python-dotenv requests pyyaml

# 환경변수 설정
cp .env.example .env  # 또는 직접 생성
# .env 파일에 API 키 설정
```

### 2. 자동 설정 스크립트 실행

```bash
bash src/scripts/setup-environment.sh
```

### 3. Solar Open 2 API 키 발급

- [Upstage Console](https://console.upstage.ai)에서 API 키 발급
- 발급된 키를 `.env` 파일의 `SOLAR_API_KEY`에 설정

### 4. 첫 실험 시작

1. `docs/experiments/`에 새 실험 파일 생성
2. `docs/templates/template-experiment.md` 참고
3. 실험 진행 후 결과 기록
4. `docs/experiments/experiment-log.md`에 일지 업데이트

## 📋 실험 워크플로우

```
1. 계획 → 2. 실행 → 3. 기록 → 4. 분석 → 5. 공유
```

### 단계별 가이드

| 단계 | 할 일 | 위치 |
|------|-------|------|
| **계획** | 실험 목적, 가설, 방법 정의 | `docs/experiments/` 새 파일 |
| **실행** | Solar Open 2 API 호출, 결과 수집 | `src/examples/`, `data/raw/` |
| **기록** | OKF 포맷으로 결과 문서화 | `docs/experiments/`, `docs/notes/` |
| **분석** | 결과 비교, 인사이트 도출 | `docs/notes/projects/` |
| **공유** | README 업데이트, GitHub Push | `README.md`, git commit |

## 📝 일일 작업 기록

실험 및 작업 진행 상황은 아래 형식으로 기록합니다:

### 실험 로그 (`docs/experiments/experiment-log.md`)

```markdown
## YYYY-MM-DD

### [실험명]

- **목적**: [실험 목적]
- **방법**: [사용 방법/프롬프트]
- **결과**: [관찰된 결과]
- **인사이트**: [도출된 인사이트]
- **참고**: [관련 파일 링크]
```

### 변경 이력 (`docs/log.md`)

```markdown
## YYYY-MM-DD

* **Creation**: [새로 만든 것]
* **Update**: [수정한 것]
* **Experiment**: [실험 기록]
```

## 🔧 주요 도구 연동

### Claude Code

Solar Open 2를 Claude Code의 커스텀 모델로 설정:

```bash
# Claude Code 설정
claude config set provider solar-open2
claude config set api_key $SOLAR_API_KEY
claude config set model solar-10.7b-chat
```

자세한 내용: [`docs/guide/claude-code-open2.md`](docs/guide/claude-code-open2.md)

### Hermes Agent

Solar Open 2를 Hermes Agent의 백엔드 모델로 설정:

```yaml
# ~/.hermes/config.yaml
models:
  solar-open2:
    provider: openai-compatible
    endpoint: https://api.upstage.ai/v1
    api_key: ${SOLAR_API_KEY}
    model_name: solar-10.7b-chat
```

자세한 내용: [`docs/guide/hermes-agent.md`](docs/guide/hermes-agent.md)

## 📚 문서 포맷 가이드

### OKF 포맷

모든 문서는 OKF 포맷을 따릅니다:

```markdown
---
type: Model              # 필수: 문서 유형
title: 문서 제목          # 추천: 표시 이름
description: 한 줄 요약    # 추천: 요약
tags: [태그1, 태그2]      # 선택: 분류 태그
timestamp: 2026-07-17...  # 선택: 최종 수정일
---

# 본문 내용

마크다운으로 작성합니다.
```

### OKF 문서 유형

| 유형 | 용도 |
|------|------|
| `Model` | 모델 정보 (Solar Open 2 등) |
| `Paper` | 논문 요약/리뷰 |
| `Experiment` | 실험 기록 |
| `Guide` | 사용법 가이드 |
| `Person` | 연구자 프로필 |
| `Project` | 프로젝트 개요 |
| `Reference` | 참조 자료 |
| `Dataset` | 데이터셋 설명 |

자세한 내용: [`docs/guide/okf-authoring.md`](docs/guide/okf-authoring.md)

## 🔒 보안 가이드

### _private 폴더

개인정보, API 키, 자격증명 등은 `_private/` 폴더에 저장합니다:

```
_private/
├── credentials/     # API 키, OAuth 토큰
├── secrets/         # 비밀 키, 인증서
└── notes/           # 개인 메모
```

⚠️ **중요**: `_private/`는 `.gitignore`에 의해 Git 추적에서 제외됩니다. 민감한 정보는 절대 이 디렉토리에 저장하지 마세요.

### 환경변수

API 키는 `.env` 파일에 저장하고, Git에 커밋하지 않습니다:

```bash
# .env (gitignore됨)
SOLAR_API_KEY=your-api-key-here
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

## 🤝 기여 가이드

1. 새 실험/문서 생성 시 OKF 포맷 준수
2. `_private/`에 민감 정보 저장 (git 제외 확인)
3. 의미 있는 커밋 메시지 작성
4. 실험 결과는 `docs/experiments/`에 기록
5. 변경 사항은 `docs/log.md`에 기록

## 📝 커밋 메시지 규칙

```
feat: 새 기능/실험 추가
fix: 버그 수정
docs: 문서 업데이트
refactor: 코드/문서 리팩토링
chore: 설정/스크립트 업데이트
```

예시:
```
feat: Solar Open 2 한국어 성능 벤치마크 실험
fix: OKF 템플릿 timestamp 형식 수정
docs: Claude Code 연동 가이드 추가
```

## ❓ 도움 받기

- 문제 발생 시: [`docs/guide/troubleshooting.md`](docs/guide/troubleshooting.md)
- OKF 포맷 문의: [`docs/guide/okf-authoring.md`](docs/guide/okf-authoring.md)
- 모델 정보: [`docs/reference/solar-open2.md`](docs/reference/solar-open2.md)
- 시작 가이드: [`docs/guide/getting-started.md`](docs/guide/getting-started.md)

## 📄 라이선스

이 작업 공간의 문서는 OKF 포맷을 따르며, Solar Open 2 모델 사용 시 Upstage의 이용 약관을 준수합니다.

---

*마지막 업데이트: 2026-07-17*
*작성자: Solar Open 2 테스트 팀*
