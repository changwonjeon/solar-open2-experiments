# Agents Rules — Ralphthon

## Source 계층
- `source/codex-original/`은 읽기 전용입니다. 내용을 수정하거나 덮어쓰지 마십시오.
- 새 source ingest 시 `docs/ralphthon/index.md`와 `docs/ralphthon/log.md`를 갱신하십시오.

## Wiki 계층
- `docs/ralphthon/`는 OKF Wiki입니다. 모든 문서에 `type` frontmatter를 포함하십시오.

## Output 계층
- `output/`은 생성 산출물입니다. source를 수정하거나 output으로 덮어쓰지 마십시오.

## 이동 규칙
- 대량 이동은 사용자 승인이 필요합니다.
- 원본 복구 시 반드시 `git hash-object`로 blob ID 일치를 확인하십시오.

## 보호 범위
- `_private/`, `_inbox/`, ignored 파일을 수정하지 마십시오.
- `git add`/`commit`/`push`는 사용자 승인 후에만 실행하십시오.
