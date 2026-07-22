# Step 1: 현재 상태 동결 및 복구 매핑 작성

## 목적

7024b1b^ 커밋의 `docs/experiments/ralphthon/` 디렉토리 상태를 완전히 감사하고, 현재 작업트리와의 차이를 매핑하여 복구 대상이 명확히 식별되도록 합니다.

## 실행 절차

### 1. 기준 커밋(7024b1b^) 상태 스냅샷 생성

```bash
git ls-tree -r 7024b1b^ -- docs/experiments/ralphthon/ > /tmp/step1-ralpthon-tree.txt
```

- 모든 blob ID, 파일 경로, 크기 목록 확보
- 중복 파일(.codex/.codex, .omx/.omx 중첩) 식별

### 2. HEAD(현재) 상태 비교

```bash
git ls-tree -r HEAD -- docs/experiments/ralphthon/ > /tmp/step1-head-tree.txt
diff -u /tmp/step1-ralpthon-tree.txt /tmp/step1-head-tree.txt > /tmp/step1-diff.txt
```

- 삭제된 파일, 추가된 파일, 변경된 파일 분류
- 중복 nesting 파일(.codex가 .codex 내에 있는 경우 등) 식별

### 3. 복구 매핑 작성

다음 형식의 매핑 테이블 생성:

| # | 기준 경로 (7024b1b^) | 현재 상태 | blob ID | 크기 | 복구 대상 위치 | 비고 |
|---|---------------------|-----------|---------|------|----------------|------|
| 1 | docs/experiments/ralphthon/fixtures/*.json | HEAD 미존재 | abc123... | 4,096 | tasks/01-ralpthon/source/codex-original/fixtures/ | 원본 |
| ... | ... | ... | ... | ... | ... | ... |

### 4. 보호 대상 검증

```bash
git ls-tree -r HEAD -- tasks/02-meeting-minutes/ > /tmp/step1-meeting-minutes.txt
```

- 원본 9개 파일, 회의록, LinkedIn 산출물 상태 확인
- `tasks/02-meeting-minutes/` 보호 대상 무결성 확인

### 5. 감사 결과 요약

```markdown
## Step 1 감사 결과

- 7024b1b^의 docs/experiments/ralphthon/에서 **N개 파일** 확인
- 고유 blob **N개** 중 **N개**가 현재 작업트리에 존재하지 않음 (git 객체 DB에는 존재)
- HEAD 대비 **N개 파일 삭제 예정**, 그중 **N개 중복 nesting(.codex/.codex, .omx/.omx)
- **N개 파일**이 이미 tasks/01-ralpthon/docs/ralpthon/으로 이동 완료 (blob 보존됨)
- 보호 대상 tasks/02-meeting-minutes/는 변경 없음 확인
```

## 검증 게이트

- [ ] 7024b1b^의 모든 파일이 감사 목록에 포함되었는가?
- [ ] 중복 nesting 파일이 모두 식별되었는가?
- [ ] 보호 대상(tasks/02-meeting-minutes/) 변경 없음이 확인되었는가?
- [ ] 복구 매핑 테이블이 완성되었는가?

## 산출물

- `/tmp/step1-ralpthon-tree.txt` — 기준 커밋 스냅샷
- `/tmp/step1-head-tree.txt` — 현재 HEAD 스냅샷
- `/tmp/step1-diff.txt` — 차이점 diff
- `tasks/03-wiki-restructure/work-log.md` — 감사 결과 기록
