# Upstage Solar Open2 테스트 작업 공간 — 에이전트 규칙

이 문서는 에이전트가 따르는 실행 규칙이다. 사람은 `README.md`를 참고하고, 에이전트는 이 파일을 따른다.

## 폴더 구조

```
_upstage/
├── _private/                      # 🔒 개인정보, 자격증명 (gitignore 됨)
│   ├── credentials/
│   ├── secrets/
│   └── notes/                     # 개인 메모 (gitignore 됨)
├── tasks/                         # 📦 실험 태스크 (Source + Wiki 분리)
│   ├── 01-ralpthon/               # 랄프톤 실험 (Ralph Loop 재현)
│   │   ├── source/                # Source 계층 — Codex 원본 및 Solar 적응 코드
│   │   │   ├── codex-original/    # Codex 원본 (77개 파일, 읽기 전용)
│   │   │   └── solar-adaptation/  # Solar 적응 코드 (선택)
│   │   ├── docs/ralpthon/         # Wiki 계층 — 실험 결과, 분석, 가이드
│   │   ├── output/                # 생성 산출물
│   │   ├── data/                  # 실험 데이터
│   │   ├── AGENTS.md              # 태스크 로컬 규칙 (Schema)
│   │   ├── CLAUDE.md              # 태스크 로컬 지시 (Schema)
│   │   └── README.md              # 태스크 설명
│   └── 02-meeting-minutes/        # 회의록 작성 실험
│       ├── source/                # Source 계층 — 회의록 원문
│       │   └── original/          # 9개 원문 (읽기 전용)
│       ├── docs/meeting-minutes/  # Wiki 계층 — 회의록, 실험 결과
│       ├── output/                # 생성 산출물 (LinkedIn 포스트 포함)
│       ├── data/                  # 실험 데이터
│       ├── AGENTS.md              # 태스크 로컬 규칙 (Schema)
│       ├── CLAUDE.md              # 태스크 로컬 지시 (Schema)
│       └── README.md              # 태스크 설명
├── docs/                          # 📚 프로젝트 공통 OKF Wiki 번들
│   ├── guide/                     # 사용법 가이드 (선택)
│   ├── reference/                 # 기술 참조 문서 (선택)
│   ├── notes/                     # LLM-Wiki 스타일 위키 (선택)
│   ├── templates/                 # 문서 템플릿 (선택)
│   ├── experiment-log.md          # 실험 일지
│   ├── log.md                     # 변경 이력
│   ├── index.md                   # 루트 인덱스
│   └── AGENTS.md                  # 위키 전용 로컬 규칙 (Schema)
├── src/                           # 💻 코드 및 스크립트
│   └── scripts/
│       └── ralphthon/             # 랄프톤 실행 스크립트
│           ├── original/          # Codex 원본 스크립트 (참조용)
│           └── (Solar 적응 스크립트들)
├── assets/                        # 🖼️ 정적 자산 (이미지 등)
├── _inbox/                        # 📥 전달용 폴더
├── AGENTS.md                      # 루트 에이전트 규칙 (이 파일, Schema)
├── CLAUDE.md                      # 루트 Claude 지시 (Schema, @AGENTS.md 참조)
├── README.md                      # 사람용 문서
└── pyproject.toml
```

## 계층 원칙 (현재 구조)

1. **Source 계층**
   - `tasks/01-ralpthon/source/codex-original/` — Codex 원본 스크립트·테스트·픽스처 (77개 파일, 읽기 전용, 불변성 보장)
   - `tasks/01-ralpthon/source/solar-adaptation/` — Solar 적응 코드 (개발 중, 수정 가능)
   - `tasks/02-meeting-minutes/source/original/` — 회의록 원문 9개 (읽기 전용, 불변성 보장)
   - `src/scripts/ralpthon/original/` — Codex 원본 스크립트 (참조용)
   - Source 파일은 내용을 수정하지 않고 참고만 한다.

2. **Wiki 계층**
   - `tasks/01-ralpthon/docs/ralpthon/` — 랄프톤 실험 Wiki (OKF 포맷)
   - `tasks/02-meeting-minutes/docs/meeting-minutes/` — 회의록 실험 Wiki (OKF 포맷)
   - `docs/` — 프로젝트 공통 Wiki (OKF 포맷)
   - Wiki 문서는 마크다운 + OKF frontmatter로 작성한다.

3. **Schema 계층**
   - 루트 `AGENTS.md` — 전체 저장소 에이전트 규칙
   - 루트 `CLAUDE.md` — 루트 Claude 지시 (`@AGENTS.md` 참조)
   - `tasks/01-ralpthon/AGENTS.md` — 랄프톤 태스크 로컬 규칙
   - `tasks/01-ralpthon/CLAUDE.md` — 랄프톤 태스크 로컬 지시
   - `tasks/02-meeting-minutes/AGENTS.md` — 회의록 태스크 로컬 규칙
   - `tasks/02-meeting-minutes/CLAUDE.md` — 회의록 태스크 로컬 지시
   - `docs/AGENTS.md` — 위키 전용 로컬 규칙
   - Schema 파일(`AGENTS.md`, `CLAUDE.md`)은 OKF 콘텐츠 검사에서 제외한다.

4. **Output 계층**
   - `tasks/01-ralpthon/output/` — 랄프톤 생성 산출물
   - `tasks/02-meeting-minutes/output/` — 회의록 생성 산출물 (LinkedIn 포스트 포함)
   - Output은 Source를 수정하거나 Output으로 덮어쓰지 않는다.

## 이동 규칙

- **대량 이동**: 사용자 승인이 필요하다.
- **원본 복구**: 반드시 `git hash-object`로 blob ID 일치를 확인한다.
- **migration 중 이동**: 구조 개편 커밋(`7024b1b`, `7024b1b`) 중 Source→Source, Wiki→Wiki 이동은 허용된다.
- **평상시 Source 불변성**: migration 완료 후 Source 파일은 읽기 전용으로 유지한다.
- **평상시 이동 제한**: `tasks/01-ralpthon/source/codex-original/`와 `tasks/02-meeting-minutes/source/original/`의 파일은 평상시 이동·수정·삭제하지 않는다.

## 문서 포맷 (OKF)

모든 Wiki 문서는 OKF 포맷 준수:

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
| `Ralph Goal` | Ralph Loop 동결 목표 |
| `Log` | 변경 이력/기록 |

### LLM-Wiki 노트 카테고리

- **People** — 연구자, 엔지니어링, 작가 등 인물
- **Models** — 모델 아키텍처, 학습 방법, 파인튜닝 기법
- **Papers** — 논문 추적, 요약, 링크
- **Projects** — 실험 프로젝트, 태스크 기록
- **Notes (general-notes)** — 생각, 아이디어, 로그, 템플릿 문서
- **Writing** — 에세이, 블로그, 뉴스레터

## Git 사용

- `_private/`는 항상 `.gitignore` 처리
- `docs/`의 모든 `.md` 파일은 OKF 포맷 준수
- 커밋 시 의미 있는 커밋 메시지 작성
- `git add`/`commit`/`push`는 사용자 승인 후에만 실행

## 실험 구분

- **랄프루프 실험 (Ralph Loop)** — 1차 실험. Codex CLI의 랄프루프를 Solar Open 2 + Claude Code로 재현. 관련 자료는 `tasks/01-ralpthon/source/`, `tasks/01-ralpthon/docs/ralpthon/`, `src/scripts/ralpthon/original/`에 분리 보관.
- **회의록 작성 실험 (Meeting Minutes)** — 2차 실험. 회의록 자동 작성 및 품질 평가. 관련 문서는 `tasks/02-meeting-minutes/source/original/`, `tasks/02-meeting-minutes/docs/meeting-minutes/`에 보관.

## 보호 범위

- Source 파일 내용 수정 금지
- 실행 코드 수정 금지
- 회의록 본문과 LinkedIn output 본문 수정 금지
- `_private/`, `_inbox/`, result 파일 수정 금지
- `git add`, `commit`, `push` 금지 (사용자 승인 필요)
