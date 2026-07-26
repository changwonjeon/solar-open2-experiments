# Task 05 — Ralphthon 철자 인식 오류 재현 실험

이 태스크는 Solar Open 2 모델에서 `Ralphthon` 철자 보존·추론·교정 및 저장소 확산 현상을 재현하기 위한 실험입니다.

## 개요

- **Canonical 철자**: Ralphthon
- **Canonical slug**: ralphthon
- **관찰된 잘못된 표기**: Ralpthon, ralpthon
- **실험 횟수**: 조건별 10회 (총 60회 probe + 10회 repository trial)

## 실험 구성

### 실험 A — 철자 인식과 보존 (6조건 × 10회)

| Case | 조건 | 설명 |
|------|------|------|
| A1 | 명시적 복사 | 공식 철자가 Ralphthon이라고 명시 |
| A2 | 음차 추론 | "랄프톤의 영문 철자를 써라" |
| A3 | 조어 구성 | Ralph + thon 결합 설명 |
| A4 | 오타 교정 | ralpthon과 canonical Ralphthon 제공 |
| A5 | 충돌 문맥 | 다수 오타 + 하나의 authoritative glossary |
| A6 | 지연 유지 | canonical 제시 후 중간 작업 뒤 재사용 |

### 실험 B — 저장소 오류 확산 (10회 trial)

임시 Git 저장소를 생성하여 구조 정리 task 수행 시 철자 오류가 어떻게 확산되는지 측정합니다.

## 디렉토리 구조

```
tasks/05-ralphthon-spelling-evaluation/
├── EXECUTION_PLAN.md      # 실행 명세 (Source)
├── README.md              # 이 파일
├── AGENTS.md              # 에이전트 로컬 규칙
├── CLAUDE.md              # Claude 로컬 지시
├── source/
│   ├── runner/            # 실험 실행기
│   └── scorer/            # 결과 채점기
├── data/
│   ├── cases.jsonl        # 60개 probe case (JSONL)
│   ├── manifest.json      # 실행 환경 동결 정보
│   └── raw/               # 비식별화된 원본 응답
├── output/
│   ├── summary.csv        # 채점 결과 (CSV)
│   └── summary.json       # 채점 결과 (JSON)
└── docs/ralphthon-spelling-evaluation/
    ├── index.md           # Wiki 인덱스
    └── results.md         # 실험 결과 보고서
```

## 사용 방법

```bash
# Dry-run 실행 (실제 API 호출 없이 시뮬레이션)
python -m source.runner.cli dry-run --output output/dry_run_results.json

# 특정 조건만 probe 실행
python -m source.runner.cli probe --condition A1

# 전체 실험 실행 (실제 API 호출 필요)
python -m source.runner.cli all

# 결과 채점
python -m source.scorer --input data/raw/ --output output/
```

## 보호 범위

- 기존 `tasks/01-ralphthon/`부터 `tasks/04-tokenizer-comparison/`까지 수정하지 않는다.
- `_private/`, `_inbox/`, 기존 result와 ignored 파일을 읽거나 수정하지 않는다.
- `git add`, `commit`, `push`는 사용자 승인 후에만 실행한다.

## 참고

- 실행 명세: [EXECUTION_PLAN.md](EXECUTION_PLAN.md)
- 실험 결과: [docs/ralphthon-spelling-evaluation/results.md](docs/ralphthon-spelling-evaluation/results.md)
