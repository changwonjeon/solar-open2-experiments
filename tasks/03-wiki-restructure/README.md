# Wiki 구조 재편 및 Canonical 경로 정립

## 작업 개요

- **작업명**: Wiki 구조 재편 및 Canonical 경로 정립
- **작업 ID**: 03
- **시작일**: 2026-07-23
- **브랜치**: main
- **HEAD**: 6e8c5d1
- **기준 커밋**: 7024b1b^ (구조 변경 전)
- **잘못된 구조 변경**: 7024b1b

## 작업 목적

저장소 내 실험 결과물을 task 단위로 분리하고, Source/Wiki/Output/Schema 계층을 명확히 구분하여 OKF 포맷 정합성과 canonical 경로 정합성을 확보합니다.

## 배경

`7024b1b` 커밋에서 문서 구조가 실험적으로 재편되었으나, 다음과 같은 문제가 발견되었습니다:

- **Source 원본 누락**: `docs/experiments/ralphthon/`에서 87개 파일 중 42개가 작업트리에 존재하지 않음 (git 객체 DB에는 존재)
- **docs 내 스크립트 혼입**: 소스 계층에 속해야 할 스크립트가 위키 계층에 혼재
- **중복 nesting**: `.codex/.codex`, `.omx/.omx` 등 불필요한 중첩 디렉토리 구조
- **OKF 포맷 위반**: 위키 문서에 frontmatter `type` 필드가 누락되거나 불일치
- **보호 대상 손상 위험**: `tasks/02-meeting-minutes/` 원본 9개 파일에 대한 변경 위험

## 진행 단계

총 5단계로 진행됩니다:

| 단계 | 이름 | 상태 |
|------|------|------|
| Step 1 | 감사 및 복구 매핑 작성 | ✅ 완료 |
| Step 2 | Ralphthon 원본 복구 | 🔄 진행 중 |
| Step 3 | 구조 정규화 | 미실행 |
| Step 4 | 문서·링크 정합 | 미실행 |
| Step 5 | 최종 검증 및 선택적 커밋 준비 | 미실행 |

## 계층 원칙

| 계층 | 경로 | 역할 |
|------|------|------|
| **Source** | `tasks/01-ralpthon/source/codex-original/` | 불변 원본 자료 (읽기 전용) |
| **Wiki** | `docs/` | OKF 포맷 지식 문서 (에이전트 유지관리) |
| **Output** | `tasks/03-wiki-restructure/` | 생성 산출물 |
| **Schema** | `AGENTS.md`, `CLAUDE.md` | 위키 구조/워크플로우 규칙 |

## 보호 범위

다음 항목은 어떠한 경우에도 수정하지 않습니다:

- `tasks/02-meeting-minutes/` — 원본 9개 파일, 회의록, LinkedIn 산출물
- `_private/` — 개인정보, 자격증명
- `_inbox/` — 전달용 폴더
- `src/data/results/` — 결과 데이터
- `.gitignore` 처리된 모든 파일

## 관련 작업

- `tasks/01-ralpthon/` — Ralphth폰 실험 원본 소스 복원 및 구조화 (완료)
- `tasks/02-meeting-minutes/` — 회의록 작성 실험 (완료)

## 생성 확인

모든 파일 생성 후 다음 명령으로 확인하십시오:

```bash
find tasks/03-wiki-restructure/ -type f | sort
```
