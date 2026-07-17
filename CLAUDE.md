# Upstage Solar Open2 테스트 작업 공간

이 폴더는 Upstage Solar Open2 모델을 테스트하는 작업 공간으로, Claude Code나 Hermes Agent에 Open2를 이용하고 실제 다양하게 사용할 실험 공간이다.

## 폴더 구조

```
_upstage/
├── _private/                   # 개인정보, 자격증명, 외부 유출 금지 자료
│   ├── credentials/            # API 키, 토큰 등
│   ├── secrets/                # 비밀 키, 인증서
│   └── notes/                  # 개인 메모 (gitignore 됨)
├── docs/                       # OKF 포맷 지식 번들
│   ├── guide/                  # 사용법 가이드
│   ├── reference/              # 모델 레퍼런스, 스펙
│   ├── experiments/            # 실험 기록, 결과
│   ├── notes/                  # 위키 노트 (LLM-Wiki 스타일)
│   └── templates/              # 문서 템플릿
├── src/                        # 스크립트, 예제 코드
│   ├── scripts/
│   └── examples/
├── data/                       # 데이터
│   ├── datasets/               # 데이터셋
│   ├── results/                # 실험 결과
│   └── benchmarks/             #benchmark 결과
├── assets/                     # 이미지 등 정적 자산
└── index.md                    # 번들 루트 인덱스 (OKF)
```

- `_private/` 전체는 `.gitignore`로 제외 (개인정보, 자격증명, 유출 금지 내용)
- `docs/`는 OKF(Open Knowledge Format) 포맷으로 관리: YAML frontmatter + Markdown body
- `docs/notes/`는 LLM-Wiki 스타일: People, Models, Papers, Projects, Notes 등으로 분류

## 문서 포맷 (OKF)

모든 문서는 OKF 포맷 준수:

```markdown
---
type: <Type name>              # REQUIRED (예: Model, Paper, Experiment, Guide)
title: <Optional display name>
description: <Optional one-line summary>
tags: [<tag>, <tag>, …]        # Optional
timestamp: <ISO 8601 datetime> # Optional
# 기타 producer-defined 키 가능
---

# 섹션 제목

본문 내용 (마크다운). 링크, 테이블, 코드 블록 자유롭게 사용.
```

## LLM-Wiki 노트 카테고리

- **People** — 연구자, 엔지니어링, 작가 등 인물
- **Models** — 모델 아키텍처, 학습 방법, 파인튜닝 기법
- **Papers** — 논문 추적, 요약, 링크
- **Projects** — 실험 프로젝트, 태스크 기록
- **Notes** — 생각, 아이디어, 로그
- **Writing** — 에세이, 블로그, 뉴스레터

## OKF 타입 레퍼런스

| 타입 | 용도 |
|------|------|
| `Model` | Solar Open2 등 모델 정보 |
| `Paper` | 논문 요약/리뷰 |
| `Experiment` | 실험 기록, 결과 |
| `Guide` | 사용법 가이드 |
| `Playbook` | 실행 절차 |
| `Reference` | 레퍼런스 자료 |
| `Person` | 연구자/엔지니어 |
| `Dataset` | 데이터셋 설명 |
| `Benchmark` | 벤치마크 결과 |
| `Project` | 프로젝트 개요 |

## Git 사용

- `_private/`는 항상 `.gitignore` 처리
- `docs/`의 모든 `.md` 파일은 OKF 포맷 준수
- 커밋 시 의미 있는 커밋 메시지 작성
