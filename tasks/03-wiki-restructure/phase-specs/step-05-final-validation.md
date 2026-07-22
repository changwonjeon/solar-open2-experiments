```
현재 `_Upstage` migration 결과를 최종 검증해줘.

이번 단계는 READ-ONLY 검증이다.
파일을 수정하거나 git add/commit/push하지 마라.

## Gate 1 — Git 상태

- branch와 HEAD
- tracked 수정·삭제
- untracked 전체
- ignored 파일과 보호 자료가 staging 대상에 섞일 가능성
- rename으로 인식될 수 있는 이동과 실제 삭제 구분

## Gate 2 — Source 보존

다음 기준을 blob ID로 다시 검사하라.

- `7024b1b^`의 Ralphthon 원본
- 현재 HEAD `6e8c5d1`의 Ralph project 자산
- 최종 canonical source
- 제거된 중복의 canonical 보존 위치

경로 수와 고유 blob 수를 각각 보고하라.

## Gate 3 — 보호 자료

다음의 사전 manifest와 현재 hash를 비교하라.

- `tasks/02-meeting-minutes/source/original/`
- `tasks/02-meeting-minutes/docs/meeting-minutes/`
- `tasks/02-meeting-minutes/output/`
- 기존 미추적 사용자 파일

문서 정합성 단계에서 의도적으로 metadata만 바꾼 문서는 본문 hash와 metadata 변경을 구분해 보고하라.

## Gate 4 — 구조

- Source / Wiki / Output / Schema 분리
- task root 진입점 존재
- canonical source 중복
- `.codex/.codex`, `.omx/.omx` 중복 nesting
- 실행 script의 docs 혼입
- README·AGENTS·filesystem 일치

## Gate 5 — OKF 및 링크

- 검사한 Wiki 파일 수
- frontmatter parse 성공 수
- `type` 존재 수
- schema 예외 수
- 실제 broken link 수
- placeholder와 planned link 수
- index에 누락된 실제 문서 수
- 고아 문서 수

## Gate 6 — 코드 검증

원본이나 결과를 변경하지 않는 범위에서 수행하라.

- shell script `zsh -n`
- Python source compile 또는 기존 정적 검사
- 가능한 기존 test suite
- `git diff --check`

테스트가 output이나 cache를 만들 수 있으면 임시 격리 디렉터리에서 실행하라.
실행할 수 없는 검증은 PASS로 처리하지 말고 NOT RUN으로 표시하라.

## 최종 표

| Gate | 결과 | 증거 |
| --- | --- | --- |
| 과거 Source 고유 blob 100% 보존 | PASS/FAIL | 수치 |
| HEAD 자산 고유 blob 100% 보존 | PASS/FAIL | 수치 |
| 의도하지 않은 삭제 0 | PASS/FAIL | 목록 |
| canonical 중복 0 | PASS/FAIL | 목록 |
| 보호 자료 안전 | PASS/FAIL | hash 비교 |
| Wiki OKF 위반 0 | PASS/FAIL | 수치 |
| 실제 broken link 0 | PASS/FAIL | 수치 |
| 문서-트리 불일치 0 | PASS/FAIL | 수치 |
| task 진입점 완비 | PASS/FAIL | 경로 |
| 테스트 | PASS/FAIL/NOT RUN | 명령과 결과 |
| diff check | PASS/FAIL | 결과 |
| staging 안전성 | PASS/FAIL | 제외 대상 |

하나라도 FAIL이면 commit 준비를 제안하지 말고 수정이 필요한 정확한 경로만 보고하라.

모두 PASS일 경우에만 다음 네 commit 단위의 pathspec 목록을 제안하라.

1. `restore: recover immutable Ralphthon source archive`
2. `refactor: organize experiments under task workspaces`
3. `docs: align OKF wiki and links with task structure`
4. `docs: record migration manifest and validation`

여전히 git add나 commit은 실행하지 말고 사용자 승인을 기다려라.
```
