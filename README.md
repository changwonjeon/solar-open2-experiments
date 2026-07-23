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
├── _private/                        # 🔒 개인정보, 자격증명 (git 추적 제외)
│   ├── credentials/                 # API 키, 토큰
│   ├── secrets/                     # 비밀 키, 인증서
│   └── notes/                       # 개인 메모
├── tasks/                           # 📦 실험 태스크 (Source + Wiki 분리)
│   ├── 01-ralphthon/                 # 랄프톤 실험 (Ralph Loop 재현)
│   │   ├── source/                  # Source 계층 — Codex 원본 및 Solar 적응 코드
│   │   │   └── codex-original/      # Codex 원본 (읽기 전용)
│   │   │       ├── .codex/          # Codex 스킬/에이전트 설정
│   │   │       ├── .omx/            # OMX 계획/컨텍스트
│   │   │       ├── fixtures/        # 테스트 픽스처
│   │   │       ├── project-docs/    # 프로젝트 문서
│   │   │       ├── src/             # 소스 코드
│   │   │       └── tests/           # 테스트
│   │   ├── docs/ralphthon/           # Wiki 계층 — 실험 결과, 분석, 가이드
│   │   ├── output/                  # 생성 산출물
│   │   ├── data/                    # 실험 데이터
│   │   ├── AGENTS.md                # 태스크 로컬 규칙 (Schema)
│   │   ├── CLAUDE.md                # 태스크 로컬 지시 (Schema)
│   │   └── README.md                # 태스크 설명
│   ├── 02-meeting-minutes/          # 회의록 작성 실험
│   │   ├── source/                  # Source 계층 — 회의록 원문
│   │   │   └── original/            # 9개 원문 (읽기 전용)
│   │   ├── docs/meeting-minutes/    # Wiki 계층 — 회의록, 실험 결과
│   │   ├── output/                  # 생성 산출물 (LinkedIn 포스트 포함)
│   │   ├── data/                    # 실험 데이터
│   │   ├── AGENTS.md                # 태스크 로컬 규칙 (Schema)
│   │   ├── CLAUDE.md                # 태스크 로컬 지시 (Schema)
│   │   └── README.md                # 태스크 설명
│   ├── 03-wiki-restructure/         # 위키 구조 개편 태스크
│   │   ├── phase-specs/             # 단계별 명세
│   │   ├── pipeline.md              # 파이프라인 정의
│   │   ├── work-log.md              # 작업 로그
│   │   ├── AGENTS.md                # 태스크 로컬 규칙 (Schema)
│   │   ├── CLAUDE.md                # 태스크 로컬 지시 (Schema)
│   │   └── README.md                # 태스크 설명
│   └── 04-tokenizer-comparison/     # 토크나이저 비교 태스크
│       ├── source/                  # Source 계층
│       │   └── original/            # 원본 애플리케이션, 검증 스크립트, 토크나이저 자산
│       │       ├── models/          # 다운로드한 토크나이저 모델
│       │       ├── app.py           # 토크나이저 비교 앱
│       │       ├── verify_models.py # 모델 검증 스크립트
│       │       └── requirements.txt
│       ├── docs/tokenizer-comparison/# Wiki 계층 — OKF 문서
│       ├── output/                  # 생성 산출물
│       ├── data/                    # 실험 데이터
│       ├── AGENTS.md                # 태스크 로컬 규칙 (Schema)
│       ├── CLAUDE.md                # 태스크 로컬 지시 (Schema)
│       └── README.md                # 태스크 설명
├── docs/                            # 📚 프로젝트 공통 OKF Wiki 번들
│   ├── guide/                       # 사용법 가이드
│   │   ├── claude-code-open2.md
│   │   ├── getting-started.md
│   │   ├── hermes-agent.md
│   │   ├── index.md
│   │   ├── okf-authoring.md
│   │   └── troubleshooting.md
│   ├── reference/                   # 기술 참조 문서
│   │   ├── index.md
│   │   └── solar-open2.md
│   ├── notes/                       # LLM-Wiki 스타일 위키
│   │   ├── index.md
│   │   ├── general-notes/
│   │   ├── models/
│   │   ├── papers/
│   │   ├── people/
│   │   ├── projects/
│   │   └── writing/
│   ├── templates/                   # 문서 템플릿
│   │   ├── template-experiment.md
│   │   ├── template-model.md
│   │   ├── template-paper.md
│   │   ├── template-person.md
│   │   └── template-project.md
│   ├── experiment-log.md            # 실험 일지
│   ├── log.md                       # 변경 이력
│   ├── index.md                     # 루트 인덱스
│   ├── AGENTS.md                    # 위키 전용 로컬 규칙 (Schema)
│   └── CLAUDE.md                    # 위키 로컬 Claude 지시 (Schema)
├── src/                             # 💻 코드 및 스크립트
│   ├── data/
│   │   └── results/
│   │       └── ralphthon/           # 랄프톤 실험 결과 데이터
│   └── scripts/
│       ├── setup-environment.sh     # 환경 설정 스크립트
│       └── ralphthon/               # 랄프톤 실행 스크립트
│           ├── original/            # Codex 원본 스크립트 (참조용)
│           ├── capture-checkpoints.sh
│           ├── compare.py
│           ├── record-session.sh
│           ├── run-ralph-direct.sh
│           ├── run-ralph-solar.sh
│           ├── ralph-deadline-watchdog.sh
│           ├── start-ralph-loop.sh
│           └── start-ralph-solar.sh
├── assets/                          # 🖼️ 정적 자산 (이미지 등)
├── _inbox/                          # 📥 전달용 폴더
├── .gitignore
├── AGENTS.md                        # 루트 에이전트 규칙 (Schema)
├── CLAUDE.md                        # 루트 Claude 지시 (Schema, @AGENTS.md 참조)
├── README.md                        # 이 파일
└── pyproject.toml
```

> **참고**: 과거 구조(`projects/ralph-loop/`, `docs/experiments/ralphthon/`, `docs/experiments/meeting-minutes/`, 전역 `tests/`, `data/fixtures/`)는 2026-07-23 구조 개편 커밋(`7024b1b`)에서 `tasks/` 체계로 재편되었습니다. 과거 경로의 문서는 현재 `tasks/01-ralphthon/docs/ralphthon/` 및 `tasks/02-meeting-minutes/docs/meeting-minutes/`에 있습니다.

## 📊 Solar Open 2 모델 정보

| 항목 | 내용 |
|------|------|
| **모델명** | Solar Open2 250B (MoE, 15B active) |
| **컨텍스트** | 1M 토큰 |
| **지원 언어** | 한국어, 영어, 일본어 |
| **라이선스** | upstage-solar-license |
| **HuggingFace** | https://huggingface.co/upstage/Solar-Open2-250B |
| **API 엔드포인트** | https://api.upstage.ai/v1 |
| **문서** | https://docs.upstage.ai/ |

> **참고**: MoE(321개 전문가) 구조로 토큰당 15B 활성 파라미터만 사용하여, 250B 전체 모델 대비 훨씬 적은 VRAM으로 대규모 추론이 가능합니다. 상세 사양은 [HuggingFace 모델 카드](https://huggingface.co/upstage/Solar-Open2-250B)를 참고하세요.

## 🧪 Solar Open 2 비교 실험 프로젝트

### 🔹 Task 01: 랄프톤(Ralphthon) 재현 실험

**폴더**: `tasks/01-ralphthon/` | **상태**: 🟡 진행 중 (Checkpoint 검증 완료, 3시간 본 실행 대기)
**실험 유형**: Codex CLI의 랄프루프(Ralph Loop)를 Solar Open 2 + Claude Code로 재현하여 자율 실행 능력 비교

랄프톤 해커톤(ICML 2026)에서 Codex CLI가 3시간 동안 자율적으로 수행한 **랄프루프(Ralph Loop)**를 Solar Open 2(Claude Code CLI)로 재현하여 두 모델의 자율 실행 능력을 정량·정성 비교합니다.

#### 📌 실험 설계

| 항목 | Codex (원본) | Solar Open2 (재현) |
|------|-------------|-------------------|
| 백엔드 모델 | Codex CLI | Solar Open2 (Claude Code) |
| 실행 명령 | `codex -a never -s workspace-write -C $ROOT "$task_text"` | `claude-upstage --allow-dangerously-skip-permissions -p "$task_text"` |
| 프롬프트 | `$ralph\n\n<RALPH_GOAL.md>` | `$ralph\n\n<RALPH_GOAL.md>` |
| 실행 시간 | ~3시간 | Phase 4에서 측정 예정 |
| P0 항목 수 | 14개 | 14개 |
| Mock 논문 수 | 10편 (3회 반복) | 10편 (3회 반복) |
| 비교 일자 | 2026-07-12 | 2026-07-17 (Phase 4 실행일) |

#### 📊 진행 상황 (2026-07-23 기준)

| 항목 | 상태 | 비고 |
|------|------|------|
| **스크립트 안정화** | ✅ 완료 | `preflight.sh`·`commit-gate.sh` 9개 항목 일관성 보정 + Git 히스토리 정리 |
| **Blocker 7건 수정** | ✅ 완료 | 종료코드 소멸, 경로 containment 게이트, null sentinel 복원, argv 전달, zsh 호환 등 |
| **정적 검증** | ✅ 완료 | `zsh -n`·`git diff --check` 통과 |
| **함수 검증 (First Checkpoint)** | ✅ 완료 | `/tmp` 격리 Git 저장소 + 로컬 bare upstream에서 Gate 0~8 전체 통과 |
| **3시간 본 실행** | ⏳ 대기 중 | 후속 checkpoint·재시도·10분 soak·30분 rehearsal 후 실행 예정 |
| **P0 완료율** | ⏳ 미측정 | Codex 14/14(100%) vs Solar Open2 — 본 실행 결과에 따라 측정 |

#### 📁 주요 산출물

- [`tasks/01-ralphthon/docs/ralphthon/solar-vs-codex-comparison.md`](tasks/01-ralphthon/docs/ralphthon/solar-vs-codex-comparison.md) — 정성·정량 비교 분석 리포트 (템플릿, 본 실행 후 채움)
- [`tasks/01-ralphthon/docs/ralphthon/RALPH_GOAL.md`](tasks/01-ralphthon/docs/ralphthon/RALPH_GOAL.md) — 랄프루프 Goal 명세 (14개 P0 항목)
- [`tasks/01-ralphthon/docs/ralphthon/context-notes.md`](tasks/01-ralphthon/docs/ralphthon/context-notes.md) — Track 2 준비 과정의 결정과 근거

#### 🚧 다음 단계

1. 후속 checkpoint 검증 (whitespace·Unicode 경로, 실패 후 index cleanup)
2. 승인되지 않은 경로 거부 검증
3. Runtime recorder·monitor·watchdog 연결
4. 10분 soak 테스트 + 30분 rehearsal
5. **3시간 본 실행** (Ralph Loop)
6. P0 완료율/schema 준수율/시간 지표 채우기

---

### 🔹 Task 02: 회의록 작성 실험

**폴더**: `tasks/02-meeting-minutes/` | **상태**: 🟢 완료
**실험 유형**: Solar Open 2의 자연어 이해·정보 추출·구조화 작성 능력을 회의록 작성 태스크로 검증

행사 개요 문서 1건과 Tiro 노트테이킹 앱의 세션별 정리 문서 8건을 입력으로 받아, Solar Open 2(Claude Code CLI)가 이를 종합·구조화·요약하여 OKF 포맷의 회의록으로 변환합니다.

#### 📌 실험 결과

- **입력**: `source/original/` 9개 파일 — 행사개요 txt 1건 + 세션별 정리 md 8건
  - 발표자: Sung Kim CEO, 이활석 CTO, 김태호 NotaAI CTO, 이태호 Upstage, Ria Upstage, 이상후 로엔컴퍼니, 김진중 Playmore, 조코딩 Q&A
- **출력**:
  - [`20260722-solar-open-weight-day.md`](tasks/02-meeting-minutes/docs/meeting-minutes/20260722-solar-open-weight-day.md) — 8개 세션 종합 회의록 (행사 개요, 진행 일정, 세션별 상세 요약, 결정사항/액션아이템 10건, 종합 인사이트 포함)
  - [`20260722-qa-session.md`](tasks/02-meeting-minutes/docs/meeting-minutes/20260722-qa-session.md) — 조코딩 Q&A 세션 심층 회의록 (패널 토론 집중 기록)

#### 📊 품질 평가 (4차원)

| 차원 | 평가 | 세부 내용 |
|------|------|----------|
| **정보 추출** | ✅ 양호 | 9개 파일 전체 핵심 내용 누락 없이 포착 (모델 아키텍처 4요소, NotaAI 3기술, 활용사례 4건, Q&A 11개 주제) |
| **구조화** | ✅ 양호 | 시간순 세션 → 주제별 분류 → 행동항목 테이블 → 인사이트 종합의 다층적 계층 구조 |
| **정확성** | ✅ 양호 | 수치(250B, 1M, GPU 2장, 35,000명, 80% 성능저하 등) 원문 유지. 발표자명·직함 정확도 확인 |
| **OKF 준수** | ✅ 양호 | `type: Experiment`, `tags`, `timestamp`, `input_sources` frontmatter 완전 준수 |

#### 📁 주요 산출물

- [`tasks/02-meeting-minutes/docs/meeting-minutes/20260722-solar-open-weight-day.md`](tasks/02-meeting-minutes/docs/meeting-minutes/20260722-solar-open-weight-day.md) — 종합 회의록
- [`tasks/02-meeting-minutes/docs/meeting-minutes/20260722-qa-session.md`](tasks/02-meeting-minutes/docs/meeting-minutes/20260722-qa-session.md) — Q&A 세션 회의록
- [`tasks/02-meeting-minutes/output/`](tasks/02-meeting-minutes/output/) — LinkedIn 포스트 등 추가 산출물

#### 🚧 다음 단계

- 실험 개요 문서 작성 (`experiment-overview.md`)
- 품질 평가 지표 체계화

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

### 🔹 Task 03: Wiki 구조 재편 및 Canonical 경로 정립

**폴더**: `tasks/03-wiki-restructure/` | **상태**: 🟢 완료
**실험 유형**: 저장소 내 실험 결과물을 task 단위로 분리하고, Source/Wiki/Output/Schema 계층을 명확히 구분하여 OKF 포맷 정합성과 canonical 경로 정합성을 확보

`7024b1b` 커밋에서 문서 구조가 실험적으로 재편되면서 발생한 Source 원본 누락, docs 내 스크립트 혼입, 중복 nesting, OKF 포맷 위반, 보호 대상 손상 위험 등의 문제를 5단계에 걸쳐 해결했습니다.

#### 📌 작업 개요

| 항목 | 내용 |
|------|------|
| **작업명** | Wiki 구조 재편 및 Canonical 경로 정립 |
| **시작일** | 2026-07-23 |
| **HEAD** | 6e8c5d1 |
| **기준 커밋** | 7024b1b^ (구조 변경 전) |

#### 📌 진행 단계 (총 5단계)

| 단계 | 이름 | 상태 |
|------|------|------|
| Step 1 | 감사 및 복구 매핑 작성 | ✅ 완료 |
| Step 2 | Ralphthon 원본 복구 | ✅ 완료 (100개 파일 복구, `git hash-object`로 blob ID 일치 확인) |
| Step 3 | 구조 정규화 | ✅ 완료 (.codex/.codex 중첩 0, .omx/.omx 중첩 0, docs/ 내 스크립트 0) |
| Step 4 | 문서·링크 정합 | ✅ 완료 (OKF frontmatter 3개 추가, broken link 6개 수정, planned 마커 제거) |
| Step 5 | 최종 검증 및 선택적 커밋 준비 | ✅ 완료 (모든 gate PASS) |

#### 📌 계층 원칙

| 계층 | 경로 | 역할 |
|------|------|------|
| **Source** | `tasks/01-ralphthon/source/codex-original/` | 불변 원본 자료 (읽기 전용) |
| **Wiki** | `docs/` | OKF 포맷 지식 문서 (에이전트 유지관리) |
| **Output** | `tasks/03-wiki-restructure/` | 생성 산출물 |
| **Schema** | `AGENTS.md`, `CLAUDE.md` | 위키 구조/워크플로우 규칙 |

#### 🚧 보호 범위

- `tasks/02-meeting-minutes/` — 원본 9개 파일, 회의록, LinkedIn 산출물
- `_private/` — 개인정보, 자격증명
- `_inbox/` — 전달용 폴더
- `src/data/results/` — 결과 데이터
- `.gitignore` 처리된 모든 파일

---

### 🔹 Task 04: Tokenizer Comparison

**폴더**: `tasks/04-tokenizer-comparison/` | **상태**: ⏳ 준비 중
**실험 유형**: 여러 오픈웨이트 모델의 토크나이저 결과를 비교하여 토큰화 패턴·효율성·호환성을 분석

다양한 오픈웨이트 모델의 토크나이저를 동일한 입력 텍스트에 적용하여, 토큰 수·토큰 분포·특수 토큰 처리·모델 간 호환성 등을 비교 분석합니다.

#### 📌 구조

| 항목 | 내용 |
|------|------|
| `source/original/` | 원본 애플리케이션, 검증 스크립트, 토크나이저 자산 (읽기 전용) |
| `docs/tokenizer-comparison/` | OKF Wiki 문서 |
| `output/` | 생성 산출물 |
| `AGENTS.md`, `CLAUDE.md` | 태스크 로컬 규칙 |

> **참고**: `source/original/` 내용은 읽기 전용으로 유지합니다.

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

---

## ⚠️ 특이사항: Ralphthon 표기 정정

공식 영문 표기는 **Ralphthon**이며 경로에는 `ralphthon`을 사용합니다. Solar Open 2 작업 과정에서 잘못된 `ralpthon` 표기가 task·Wiki·실행 스크립트·Skill·결과 폴더로 반복 확산돼, 2026-07-23 Codex가 사용자 지시에 따라 현재 경로와 참조를 전수 정정했습니다.

이 사례는 초기 고유명사 오류가 대규모 파일 작업에서 일관되게 복제될 수 있음을 보여줍니다. 향후 migration에서는 canonical 명칭 사전과 금지 문자열 전수 검색을 완료 gate로 사용합니다. Git 이력과 전체 정정 범위는 [`Ralphthon 표기 오류 정정 기록`](docs/notes/general-notes/ralphthon-spelling-correction.md)에 보존합니다.
