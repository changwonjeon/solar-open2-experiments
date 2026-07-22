# Step 2: Ralphthon 원본만 복구

## 목적

7024b1b^ 커밋에서 `docs/experiments/ralphthon/`에 존재했던 원본 파일(fixtures, src, tests, .codex, .omx) 중 HEAD에 존재하지 않는 파일들을 `tasks/01-ralpthon/source/codex-original/`에 복원합니다.

## 보호 대상

- `tasks/02-meeting-minutes/` — 절대 수정하지 않음
- `_private/`, `_inbox/`, `src/data/results/`, ignored 파일 — 수정 금지
- `tasks/01-ralpthon/source/codex-original/` 내 기존 파일은 git hash-object로 보존 확인 후 이동

## 실행 절차

### 1. 복구 대상 식별

```bash
# Step 1에서 생성한 매핑 테이블 참조
# 다음 유형의 파일만 복구 대상으로 지정:
# - fixtures/*.json
# - src/**
# - tests/**
# - .codex/**
# - .omx/**
```

### 2. blob ID 검증 후 복구

각 복구 대상 파일에 대해:

```bash
# 1. git 객체 DB에서 blob ID 확인
git rev-parse 7024b1b^:<filepath>

# 2. 현재 작업트리에서 해당 경로에 이미 파일이 있는지 확인
ls -la <target-path>

# 3. 기존 파일이 있다면 hash-object로 보존 확인
git hash-object <existing-file>

# 4. blob ID가 일치하면 덮어쓰기하지 않고, 불일치하면 백업 후 복원
git show 7024b1b^:<filepath> > <target-path>
```

### 3. 복구 실행

```bash
# tasks/01-ralpthon/source/ 디렉토리 생성
mkdir -p tasks/01-ralpthon/source/codex-original/

# fixtures 복구
git show 7024b1b^:docs/experiments/ralphthon/fixtures/*.json > tasks/01-ralpthon/source/codex-original/fixtures/ 2>/dev/null || true

# src 복구
git show 7024b1b^:docs/experiments/ralphthon/src/** > tasks/01-ralpthon/source/codex-original/src/ 2>/dev/null || true

# tests 복구
git show 7024b1b^:docs/experiments/ralphthon/tests/** > tasks/01-ralpthon/source/codex-original/tests/ 2>/dev/null || true

# .codex 복구
git show 7024b1b^:docs/experiments/ralphthon/.codex/** > tasks/01-ralpthon/source/codex-original/.codex/ 2>/dev/null || true

# .omx 복구
git show 7024b1b^:docs/experiments/ralphthon/.omx/** > tasks/01-ralpthon/source/codex-original/.omx/ 2>/dev/null || true
```

### 4. 중복 nesting 파일 처리

- `.codex/.codex/**` → `.codex/**`로 flat하게 복원
- `.omx/.omx/**` → `.omx/**`로 flat하게 복원
- 중첩된 디렉토리는 무시하고 실제 파일만 추출

### 5. 검증 게이트

```bash
# 원본 blob 보존 검증
find tasks/01-ralpthon/source/codex-original/ -type f | while read f; do
  blob_id=$(git hash-object "$f")
  echo "$blob_id  $f"
done > /tmp/step2-recovery-blobs.txt

# HEAD 삭제 자산 보존 검증
# Step 1 매핑 테이블의 모든 파일이 복구되었는지 확인
```

## 검증 게이트 (최종)

- [ ] **G1**: 원본 blob 보존율 100% — Step 1에 식별된 모든 blob이 복구되었는가?
- [ ] **G2**: HEAD 삭제 자산 보존 100% — HEAD에서 삭제된 모든 자산이 복구되었는가?
- [ ] `tasks/02-meeting-minutes/` 보호 자료의 hash가 예상과 같은가?

## 산출물

- `tasks/01-ralpthon/source/codex-original/` — 복원된 원본 파일들
- `/tmp/step2-recovery-blobs.txt` — 복구된 blob ID 목록
- `tasks/03-wiki-restructure/work-log.md` — 복구 결과 기록
