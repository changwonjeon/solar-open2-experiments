# Upstage Solar Open 2 테스트 작업 공간

> **Solar Open 2**는 Upstage에서 제공하는 오픈소스 대형 언어 모델입니다. 이 작업 공간은 Solar Open 2를 Claude Code, Hermes Agent와 연동하여 다양한 사용 사례를 실험하고, 그 결과를 OKF(Open Knowledge Format) 포맷으로 체계적으로 문서화하는 공간입니다.

## 🎯 프로젝트 목적

- Solar Open 2 모델의 다양한 기능 실험 및 검증
- Claude Code / Hermes Agent와의 연동 테스트
- 실험 결과, 발견사항, 인사이트를 OKF 포맷으로 축적
- LLM-Wiki 스타일의 지식 베이스 구축

## 📁 폴더 구조

```
_upstage/
├── _private/                      # 🔒 개인정보, 자격증명 (git 추적 제외)
│   ├── credentials/               # API 키, 토큰
│   ├── secrets/                   # 비밀 키, 인증서
│   └── notes/                     # 개인 메모
├── docs/                          # 📚 OKF 포맷 지식 번들
│   ├── guide/                     # 사용법 가이드
│   │   ├── getting-started.md     # 시작 가이드
│   │   ├── claude-code-open2.md   # Claude Code 연동
│   │   ├── hermes-agent.md        # Hermes Agent 연동
│   │   ├── okf-authoring.md       # OKF 문서 작성법
│   │   └── troubleshooting.md     # 문제 해결
│   ├── reference/                 # 기술 참조 문서
│   │   ├── solar-open2.md         # Solar Open 2 상세 스펙
│   │   └── index.md
│   ├── experiments/               # 실험 기록
│   │   ├── experiment-log.md      # 실험 일지
│   │   └── index.md
│   ├── notes/                     # LLM-Wiki 스타일 위키
│   │   ├── people/                # 연구자 프로필
│   │   ├── models/                # 모델 문서
│   │   ├── papers/                 # 논문 요약
│   │   ├── projects/              # 프로젝트 기록
│   │   ├── notes/                 # 아이디어/로그
│   │   └── writing/               # 에세이/블로그
│   ├── templates/                 # 문서 템플릿
│   │   ├── template-model.md
│   │   ├── template-paper.md
│   │   ├── template-experiment.md
│   │   ├── template-person.md
│   │   └── template-project.md
│   ├── index.md                   # 루트 인덱스
│   └── log.md                     # 변경 이력
├── src/                           # 💻 코드 및 스크립트
│   ├── scripts/                   # 유틸리티 스크립트
│   └── examples/                  # 예제 코드
├── data/                          # 📊 데이터
│   ├── datasets/                  # 데이터셋
│   ├── results/                   # 실험 결과
│   └── benchmarks/                # 벤치마크 결과
├── assets/                        # 🖼️ 정적 자산 (이미지 등)
├── .gitignore                     # Git 제외 설정
├── README.md                      # 이 파일
└── CLAUDE.md                      # Claude Code 운영 지침
```


## 📊 Solar Open 2 모델 정보

| 항목 | 내용 |
|------|------|
| **개발사** | Upstage (한국 스타트업) |
| **모델명** | Solar Open 2 |
| **파라미터** | ~10.7B |
| **컨텍스트** | 32K 토큰 |
| **아키텍처** | Decoder-only Transformer |
| **API 엔드포인트** | https://api.upstage.ai/v1 |
| **문서** | https://docs.upstage.ai/ |

## 🧪 Solar Open 2 비교 실험 프로젝트

### 랄프톤(Ralphthon) 재현 실험

랄프톤 해커톤(ICML 2026)에서 Codex CLI가 자율적으로 수행한 **랄프루프(Ralph Loop)**를 Solar Open 2 + Claude Code로 재현하여 두 모델의 자율 실행 능력을 비교 분석합니다.

**실험 개요:**
- **목표**: 랄프톤에서 Codex가 3시간 동안 autonomously 수행한 P0 deliverables를 Solar Open 2로 재현
- **프롬프트**: `$ralph\n\n<RALPH_GOAL.md>` (랄프톤의 Goal 파일 전체)
- **비교 방식**: 정성(이해도/수행력) + 과정(로그/체크포인트) + 정량(P0 완료율/schema 준수율/시간)

**실험 자료:** [`docs/notes/general-notes/ralphthon-solar-comparison.md`](docs/notes/general-notes/ralphthon-solar-comparison.md)

**진행 상태 (2026-07-20 03:52 KST):** 🟢 Git checkpoint 7개 blocker 수정 완료. 임시 Git 저장소에서 첫 checkpoint 성공 경로(full end-to-end) 검증했습니다. 후속 checkpoint·재시도·failure cleanup·runtime 연결은 다음 작업으로 남았습니다.

- **스크립트 안정화 히스토리 (2026.07.17~07.20)**:

  | 일자 | 커밋 | 내용 |
  |------|------|------|
  | 07/17 | `963d81a` | Phase 4 Question Mode 전환 및 스크립트 완전 수정 |
  | 07/18 | `bc542a1` | tmux `load-buffer` stdin `'-'` 플래그 및 watchdog root 경로 계산 수정 |
  | 07/18 | `9772ed9` | `SCRIPT_DIR/ROOT` 경로 해결 로직 강화, tmux/prompt injection 보안 강화 |
  | 07/18 | `b65b812` | `exec 2>/dev/tty` 제거 → nohup 호환 디버깅 로깅 |
  | 07/19 | `be938db` | 3개 스크립트 pure ASCII 재작성 → 멀티바이트 파싱 코럽션 완전 제거 |
  | 07/19 | `0e9f269` | tmux `load-buffer -a` 미지원 플래그 오류 수정, UTF-8 파싱 코럽션 완전 제거 |
  | 07/19 | `93f60fb` | `.gitignore` 갱신: Claude Code 일반 상태는 무시, 프로젝트 스킬(`solar-ralph`, `git-checkpoint`)만 추적; `record-session.sh` 실행 권한 부여 |
  | 07/19 | `2fcaf08` | README 및 실험로그에 07/19 안정화 내용 동기화 |
  | 07/19 | `3a15443` | Ralph Loop + git-checkpoint 스킬 파일 추가 |
  | 07/20 | `4a8d953` | **9개 항목 스킬 일관성 보정** + Git 히스토리 정리 |
  | 07/20 | `5b68b93` | **Git checkpoint blocker 7건 수정** (`preflight.sh` 종료코드·경로검증·null sentinel, `commit-gate.sh` 인자 가드·argv approved_paths·zsh `read -rA`) + `README.md`/`docs/log.md`/`docs/experiments/experiment-log.md` 동기화 |

- **03:52 KST 검증 결과 (7개 blocker 수정)**:
  - `preflight.sh`: Python 종료 코드가 `set -e`에 의해 소멸되던 문제를 `if python3 ...; then ... else RS_EXIT=$?; fi` 분기로 해결하고, `mktemp` + `trap` 정리 + temp file 디코딩으로 stdout/종료코드 분리 처리. malformed JSON·누락 필드·잘못된 타입에서 `exit 1` fail-closed 동작 확인.
  - `preflight.sh`: `--run-state` 경로를 저장소 상대 경로만 허용하고 절대 경로·대시 시작 경로·디렉터리·저장소 밖 resolve·symlink component를 `exit 1`~`exit 2`로 거부하는 경로 containment 게이트 신설. `run-state.json`은 canonical realpath(`$RS_REAL`)로 Python에 전달해 symlinked-but-resolved 경로도 정상 처리.
  - `preflight.sh`: 첫 checkpoint의 `last_checkpoint_commit: null`이 Python에서 `__NULL__` sentinel로 출력된 뒤 쉘에서 복원되지 않아 subsequent checkpoint로 오인되던 문제를 `[[ "$LAST_CHECKPOINT_COMMIT_FROM_STATE" == "__NULL__" ]] → ""` 변환으로 수정.
  - `commit-gate.sh`: `--run-state`·`--summary` 옵션 처리 시 `$2` 읽기 전 `$# -lt 2` 검사 및 stderr 오류·`exit 2` 처리 추가.
  - `commit-gate.sh`: 성공 JSON의 `approved_paths`를 heredoc stdin 대신 `sys.argv[6:]` argv slice로 전달해 공백·유니코드·대시 시작 경로가 배열 원소로 보존되도록 수정.
  - `commit-gate.sh`: Bash 전용 `read -ra`를 zsh 호환 `read -rA`로 수정(2개 위치: line 94 COMPONENTS, line 137 COMPONENT_ARRAY).
  - 정적 검증: 전체 대상 script `zsh -n`·`git diff --check` 통과. malformed JSON·누락 schema·절대·대시 시작·디렉터리·저장소 밖 run-state 경로가 예상한 non-zero 코드로 거부됨 확인. `--run-state`에 `__NULL__` sentinel 복원 전후 첫/checkpoint 판별 정상 동작 확인.
  - 함수 검증: `/tmp` 격리 Git 저장소와 로컬 bare upstream에서 first-checkpoint preflight Gate 1~4와 commit gate Gate 0~8 전체 통과. `P0-1`의 승인 경로 `deliverable.txt`만 로컬 commit에 포함되고 성공 JSON의 `approved_paths`가 정확한 배열로 출력됨 확인.
  - 범위: 외부 remote 작업 없음. 테스트용 로컬 bare repository만 사용.

- **9개 항목 일관성 보정 (2026.07.20)** — `fix/solar-ralph-skill-consistency` 브랜치:

  | 대상 파일 | 항목 | 핵심 보정 |
  |-----------|------|-----------|
  | `commit-gate.sh` | 2개 | ① 3개 Python 블록의 `os.environ['P0_ID']`/`os.environ['RUN_STATE_PATH']` → `sys.argv[1]`/`sys.argv[2]` argv 전달로 전환, ② Gate 번호를 실제 실행 순서에 맞게 0~8 재정렬 (0=인덱스폴루션, 1=승인경로검증, 2=비밀패턴검사, 3=작업트리신뢰, 4=테스트증거, 5=스테이징, 6=스테이징후검증, 7=사전커밋검증, 8=커밋+JSON출력) |
  | `preflight.sh` | 4개 | argv 기반 run-state 경로 전달(`sys.argv[1]`) 확인; 조건부 브랜치 우회 로직 없음 확인; `$# -lt 2` 옵션 가드 확인; 모든 출력이 stderr(`print -r -u2`)로 통일 확인 |
  | `SKILL.md` | 2개 | Resume 섹션의 "it may modify" 모순 문장 제거; 비수정 계약("never modifies worktree files or Git history - on success or on failure. No staging, committing, resetting, or file modification occurs as part of resume, regardless of outcome.") 명확화; "twice before" → "once already" 통일 |
  | `state-contract.md` | 1개 | `P0 Item Schema`의 `status` 필드에 `needs-operator` 추가; Resume Consistency Contract (4개 독립 비교) 문서화; Status Transitions 표에 `tests_passed`, `checkpoint_failed`, `needs-operator` 포함; State Write Distinctions(원자적 교체 vs 추가 전용) 정리 |

- **Git 히스토리 정리 (2026.07.20)**: `git rebase -i --root`를 통해 과거 7개 커밋에 포함된 Co-Authored-By 트레일러를 제거했습니다. 이전 기록에 언급된 `.gitmessage`와 `clean-coauthor.sh`는 현재 Git 이력에 존재하지 않아 후속 확인 대상으로 남겼습니다.
---

## 🚀 실행 가이드

랄프톤 실험을 바로 실행하려면:


또는  스킬을 사용하여 에이전트가 자동으로 실행할 수 있습니다.
---

## 🗓️ Stage 1 일정

| 기간 | 내용 |
|------|------|
| **2026.07.17 ~ 07.31** | Stage 1 실험 기간 (약 2주) |
| **종료 시** | GitHub 저장소 링크 + 200자 이상 후기 제출 |

## 🔗 유용한 링크

- [Upstage Console](https://console.upstage.ai)
- [Solar Open 2 API 문서](https://console.upstage.ai/api/chat)
- [OKF 포맷 스펙](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
- [LLM-Wiki (Karpathy)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
