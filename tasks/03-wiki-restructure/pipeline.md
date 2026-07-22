# Wiki 구조 재편 파이프라인

## 개요
이 파이프라인은 `_Upstage` 저장소의 Wiki 구조를 task 단위로 재편하고, Source/Wiki/Output/Schema 계층을 명확히 구분합니다.

## 파이프라인 흐름

```
[Step 1] 감사 및 복구 매핑 작성
    ↓ (승인)
[Step 2] Ralphthon 원본 복구
    ↓ (보존율 100% 확인)
[Step 3] 구조 정규화
    ↓ (canonical 중복 0 확인)
[Step 4] 문서·링크 정합
    ↓ (OKF 위반 0, broken link 0 확인)
[Step 5] 최종 검증
    ↓ (모든 gate PASS)
[승인 후] git add → git commit → git push
```

## 중단 조건
- 원본 blob 보존율이 100%가 아니면 다음 단계로 진행하지 않음
- `tasks/02-meeting-minutes/` 보호 자료의 hash가 예상과 다르면 즉시 중단

## Gate 요약
| Gate | 포함 단계 | 통과 기준 |
|------|-----------|----------|
| G1 | Step 2 | 원본 blob 보존 100% |
| G2 | Step 2 | HEAD 삭제 자산 보존 100% |
| G3 | Step 3 | canonical 중복 0 |
| G4 | Step 4 | OKF 위반 0 |
| G5 | Step 5 | 모든 gate 종합 PASS |

## 주의사항
- `tasks/02-meeting-minutes/`는 절대 수정하지 않습니다
- 모든 단계 종료 후 출력물을 `work-log.md`에 기록하십시오
- git add/commit/push는 마지막 사용자 승인 후에만 실행합니다

## 생성 확인
파일 생성 후 다음 명령으로 확인하십시오:
```bash
find tasks/03-wiki-restructure/ -type f | sort
```
