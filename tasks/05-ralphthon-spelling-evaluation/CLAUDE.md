# Claude Instructions — Ralphthon Spelling Evaluation

이 태스크에서 Claude Code는 다음 지시를 따른다.

## 실행 환경
- 모델은 `solar-open2`이다.
- 모든 probe는 `--no-session-persistence`로 새 세션에서 실행한다.
- 단순 언어 probe는 `--bare --tools ""`를 적용한다.
- 자동 fallback 모델은 사용하지 않는다.

## 실험 A — 철자 인식 (6조건 × 10회)
- A1~A6 각 조건의 case는 `data/cases.jsonl`에서 로드한다.
- 각 probe는 독립 세션에서 실행한다.
- 응답은 `data/raw/`에 원본 JSON으로 저장한다.

## 실험 B — 저장소 확산 (10회 trial)
- 격리된 임시 Git 저장소에서만 실행한다.
- 절대 경로는 raw 결과에서 제거한다.
- trial 완료 후 `_Upstage`의 기존 파일 변경 여부를 검사한다.

## 채점
- `source/scorer/`를 사용하여 exact match, Levenshtein distance, Wilson 95% CI를 계산한다.
- 동일 raw data를 다시 채점하면 byte-identical한 요약이 생성돼야 한다.
- 음차 추론(A2)과 canonical 보존 오류(A1, A3~A6)는 별도 집계한다.

## 완료 기준
- A1~A6은 조건별 10개의 독립 결과를 갖는다.
- 저장소 trial 10개가 서로 격리돼 있다.
- raw 응답, manifest, 요약 결과와 보고서 사이의 case 수가 일치한다.
- 기존 Task 01~04와 보호 대상의 hash 또는 Git diff에 변화가 없다.

## 금지 사항
- `git add`, `commit`, `push`는 사용자 승인 없이 실행하지 않는다.
- 실패한 호출을 삭제하지 않는다.
- 비밀값, API 키, 전체 홈 경로를 산출물에 기록하지 않는다.
