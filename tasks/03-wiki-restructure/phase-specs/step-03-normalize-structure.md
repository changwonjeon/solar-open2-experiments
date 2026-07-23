# Step 3: 구조 정규화

## 목적

Source/Wiki/Output/Schema 계층을 명확히 분리하고, 중복 nesting(.codex/.codex, .omx/.omx)을 제거하며, canonical 경로를 정립합니다.

## 계층 분리 원칙

| 계층 | 경로 | 역할 | 보호 수준 |
|------|------|------|-----------|
| **Source** | `tasks/01-ralphthon/source/codex-original/` | 불변 원본 자료 | 읽기 전용, 수정 금지 |
| **Wiki** | `docs/` | OKF 포맷 지식 문서 | 에이전트 유지관리 |
| **Output** | `tasks/03-wiki-restructure/` | 생성 산출물 | 결과물 기록 |
| **Schema** | `AGENTS.md`, `CLAUDE.md` | 위키 구조/워크플로우 규칙 | @AGENTS.md 참조 |

## 실행 절차

### 1. 중복 nesting 제거

```bash
# .codex/.codex 중첩 제거
find docs/experiments/ralphthon/ -path "*/.codex/.codex/*" -type f | while read f; do
  target=$(echo "$f" | sed 's|/.codex/.codex/|/.codex/|')
  mkdir -p "$(dirname "$target")"
  cp "$f" "$target"
  rm "$f"
done

# .omx/.omx 중첩 제거
find docs/experiments/ralphthon/ -path "*/.omx/.omx/*" -type f | while read f; do
  target=$(echo "$f" | sed 's|/.omx/.omx/|/.omx/|')
  mkdir -p "$(dirname "$target")"
  cp "$f" "$target"
  rm "$f"
done
```

### 2. src/scripts/ralphthon/original/ → Source 계층 이동

- `src/scripts/ralphthon/original/`의 Codex 원본 스크립트는 `tasks/01-ralphthon/source/codex-original/src/`로 이동
- `src/scripts/ralphthon/`에는 Solar 적응 스크립트만 유지

### 3. docs/ 내 스크립트 분리

- `docs/` 디렉토리에 포함된 스크립트(.py, .sh, .js 등)는 Source 계층으로 이동
- `docs/`에는 마크다운 지식 문서만 유지

### 4. Canonical 경로 정립

다음 canonical 경로를 정의:

| 리소스 | Canonical 경로 | 비고 |
|--------|---------------|------|
| Ralphthon 실험 원본 | `tasks/01-ralphthon/source/codex-original/` | 읽기 전용 |
| Ralphthon 실험 위키 | `docs/experiments/ralphthon/` | OKF 포맷 |
| Meeting Minutes 실험 | `tasks/02-meeting-minutes/` | 보호 대상 |
| Meeting Minutes 위키 | `docs/experiments/meeting-minutes/` | OKF 포맷 |
| Wiki 재구성 산출물 | `tasks/03-wiki-restructure/` | 산출물 |

### 5. 링크 경로 업데이트

- `docs/` 내 모든 마크다운 파일에서 canonical 경로가 아닌 참조를 수정
- `../`로 시작하는 상대 경로를 canonical 절대 경로로 변경

### 6. canonical 중복 검증

```bash
# 동일한 파일이 여러 경로에 존재하는지 확인
find . -name "*.md" -o -name "*.json" -o -name "*.py" -o -name "*.sh" | \
  xargs -I{} md5sum {} | sort | uniq -d -w32

# 중복 nesting 존재 여부 확인
find . -path "*/*.codex/.codex/*" -o -path "*/*.omx/.omx/*" | wc -l
# 결과: 0 이어야 함
```

## 검증 게이트

- [ ] **G3**: canonical 중복 0 — 동일한 blob이 여러 경로에 존재하지 않는가?
- [ ] 중복 nesting(.codex/.codex, .omx/.omx)이 모두 제거되었는가?
- [ ] `docs/` 내에 스크립트가 포함되지 않았는가?
- [ ] 모든 `docs/` 마크다운 파일이 OKF frontmatter를 포함하는가?

## 산출물

- 계층 분리가 완료된 저장소 구조
- Canonical 경로 매핑 테이블
- `tasks/03-wiki-restructure/work-log.md` — 정규화 결과 기록
