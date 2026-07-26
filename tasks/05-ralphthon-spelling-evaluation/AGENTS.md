# Agents Rules — Ralphthon Spelling Evaluation

## Source 계층
- `data/cases.jsonl`과 `data/manifest.json`은 실험 입력 데이터로, 수정하지 않는다.
- `source/runner/`와 `source/scorer/`는 실행기·채점기 소스로, 수정 시 사용자 승인이 필요하다.

## Wiki 계층
- `docs/ralphthon-spelling-evaluation/`는 OKF Wiki이다. 모든 문서에 `type` frontmatter를 포함하라.
- Wiki 문서는 실험 결과, 관찰, 해석, 한계를 구분하여 기록한다.

## Output 계층
- `output/`은 생성 산출물이다. source를 수정하거나 output으로 덮어쓰지 말라.
- `data/raw/`는 비식별 처리된 원본 JSON 응답을 보존한다. 수정하지 않는다.

## 이동 규칙
- 대량 이동은 사용자 승인이 필요하다.
- 원본 복구 시 반드시 `git hash-object`로 blob ID 일치를 확인하라.

## 보호 범위
- 기존 `tasks/01-ralphthon/`부터 `tasks/04-tokenizer-comparison/`까지 수정하지 말라.
- `_private/`, `_inbox/`, 기존 result와 ignored 파일을 읽거나 수정하지 말라.
- `git add`/`commit`/`push`는 사용자 승인 후에만 실행하라.
- 실험 도중 실패한 호출도 삭제하지 말고 상태와 종료 코드를 기록하라.
