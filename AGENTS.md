# Upstage Solar Open2 테스트 작업 공간 — 에이전트 규칙

이 문서는 에이전트가 따르는 실행 규칙이다. 사람은 `README.md`를 참고하고, 에이전트는 이 파일을 따른다.

## 폴더 구조

```
_upstage/
├── _private/                   # 🔒 개인정보, 자격증명 (gitignore 됨)
│   ├── credentials/
│   ├── secrets/
│   └── notes/                  # 개인 메모 (gitignore 됨)
├── projects/                   # 📦 Source 계층 — 원본 자료 보관
│   └── ralph-loop/             # 랄프루프 실험 원본 자료
├── docs/                       # 📚 OKF 포맷 지식 번들 (위키 계층)
│   ├── guide/
│   ├── reference/
│   ├── experiments/
│   │   ├── ralph-loop/
│   │   └── meeting-minutes/
│   ├── notes/
│   │   ├── people/
│   │   ├── models/
│   │   ├── papers/
│   │   ├── projects/
│   │   ├── writing/
│   │   └── general-notes/
│   ├── templates/
│   ├── index.md
│   ├── log.md
│   ├── AGENTS.md               # 위키 전용 로컬 규칙
│   └── CLAUDE.md               # @AGENTS.md 참조
├── src/                        # 💻 코드 및 스크립트
│   ├── scripts/
│   │   └── ralphthon/
│   │       ├── original/       # Codex 원본 스크립트 (참조용)
│   │       └── (Solar 적응 스크립트들)
│   └── data/
│       └── fixtures/
├── tests/                      # 🧪 테스트 (랄프톤 원본 테스트 등)
├── data/                       # 📊 데이터
│   ├── datasets/
│   │   └── ralphthon-mock/
│   ├── results/
│   │   └── ralphthon/
│   └── benchmarks/
├── assets/                     # 🖼️ 정적 자산
├── _inbox/                     # 📥 전달용 폴더
├── AGENTS.md                   # 에이전트 규칙 (이 파일)
├── CLAUDE.md                   # @AGENTS.md 참조
├── README.md                   # 사람용 문서
└── pyproject.toml
```

## 문서 포맷 (OKF)

모든 위키 문서는 OKF 포맷 준수:

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

### OKF 타입 레퍼런스

| 타입 | 용도 |
|------|------|
| `Model` | Solar Open2 등 모델 정보 |
| `Paper` | 논문 요약/리뷰 |
| `Experiment` | 실험 기록, 결과 |
| `Guide` | 사용법 가이드 |
| `Playbook` | 실행 절차 |
| `Reference` | 레퍼런스 자료 |
| `Project` | 프로젝트 개요 |
| `Person` | 연구자/엔지니어 |
| `Dataset` | 데이터셋 설명 |
| `Benchmark` | 벤치마크 결과 |
| `Ralph Context Snapshot` | Ralph Loop 컨텍스트 동결 |
| `Work Plan` | 작업 계획 |
| `Execution Specification` | 실행 명세 |
| `Context Notes` | 컨텍스트/결정 기록 |
| `Frozen Evaluation Contract` | 평가 계약 동결 |

### LLM-Wiki 노트 카테고리

- **People** — 연구자, 엔지니어링, 작가 등 인물
- **Models** — 모델 아키텍처, 학습 방법, 파인튜닝 기법
- **Papers** — 논문 추적, 요약, 링크
- **Projects** — 실험 프로젝트, 태스크 기록
- **Notes (general-notes)** — 생각, 아이디어, 로그, 템플릿 문서
- **Writing** — 에세이, 블로그, 뉴스레터

## 계층 원칙

1. **Source 계층 (projects/, src/scripts/ralpthon/original/, tests/, data/fixtures/)** — 불변 원본 자료. 수정하지 않고 참고만 한다. Codex 원본 스크립트, 테스트, 픽스처, 설정 파일이 여기 속한다.
2. **Wiki 계층 (docs/)** — 에이전트가 작성·유지관리하는 지식 문서. 마크다운 + OKF frontmatter. 실험 결과, 분석, 가이드, 노트가 여기 속한다.
3. **Schema 계층 (AGENTS.md, CLAUDE.md)** — 위키 구조/워크플로우 규칙 문서.

## Git 사용

- `_private/`는 항상 `.gitignore` 처리
- `docs/`의 모든 `.md` 파일은 OKF 포맷 준수
- 커밋 시 의미 있는 커밋 메시지 작성

## 실험 구분

- **랄프루프 실험 (Ralph Loop)** — 1차 실험. Codex CLI의 랄프루프를 Solar Open 2 + Claude Code로 재현. 관련 자료는 `docs/experiments/ralpthon/`, `projects/ralph-loop/`, `src/scripts/ralpthon/original/`에 분리 보관.
- **회의록 작성 실험 (Meeting Minutes)** — 2차 실험. 회의록 자동 작성 및 품질 평가. 관련 문서는 `docs/experiments/meeting-minutes/`에 신규 생성.
