# Upstage Solar Open2 지식 번들 — 위키 에이전트 규칙

이 폴더는 OKF 포맷 지식 번들(위키 계층)이다. 에이전트가 위키 문서를 작성·유지관리할 때 따르는 규칙이다.

## 핵심 원칙

1. **Wiki 계층만 수정한다** — `docs/` 아래의 마크다운 문서만 생성·수정한다. `src/`, `tests/`, `data/fixtures/`, `projects/`는 Source 계층으로 읽기 전용이다.
2. **모든 문서에 OKF frontmatter 필수** — `type` 필드는 반드시 포함해야 한다. `title`, `description`, `tags`, `timestamp`는 권장.
3. **원본을 복제하지 않는다** — 기존 Source 계층 자료는 `docs/`로 복사하지 말고, 필요한 경우 링크하거나 요약·분석을 작성한다.
4. **내부 링크는 상대 경로로** — `../` 기준으로 상대 경로를 사용한다.

## 위키 하위 디렉토리 규칙

| 디렉토리 | 용도 | index.md 필수 | log.md |
|----------|------|---------------|--------|
| `guide/` | 사용법 가이드 | ✅ | ❌ |
| `reference/` | 기술 참조 문서 | ✅ | ❌ |
| `experiments/ralph-loop/` | 랄프루프 실험 결과 | ✅ | ❌ (루트 log.md 참조) |
| `experiments/meeting-minutes/` | 회의록 작성 실험 결과 | ✅ | ❌ (루트 log.md 참조) |
| `notes/people/` | 인물 프로필 | ✅ | ❌ |
| `notes/models/` | 모델 문서 | ✅ | ❌ |
| `notes/papers/` | 논문 요약 | ✅ | ❌ |
| `notes/projects/` | 프로젝트 기록 | ✅ | ❌ |
| `notes/writing/` | 에세이/블로그 | ✅ | ❌ |
| `notes/general-notes/` | 아이디어/로그/컨텍스트 | ✅ | ❌ |

## 문서 생성 절차

1. 적절한 하위 디렉토리에 새 `.md` 파일 생성
2. OKF frontmatter 작성 (최소 `type` 필수)
3. 해당 디렉토리의 `index.md`에 새 문서 추가
4. 관련 문서에 상호 링크 추가
5. 루트 `log.md`에 변경 기록
