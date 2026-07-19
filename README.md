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

**실험 자료:** [`docs/notes/notes/ralphthon-solar-comparison.md`](docs/notes/notes/ralphthon-solar-comparison.md)

**진행 상태:** 🟢 Phase 1~4 완료 → Phase 5 실행 중 (결과 분석 및 비교 보고서 작성)
- **최근 개선 사항 (2026.07.19~07.20)**: Ralph Loop 스크립트 안정화 및 스킬 일관성 보정
  - `tmux load-buffer` 관련 오류 수정 및 UTF-8 파싱 코럽션 완전 제거
  - 모든 스크립트를 pure ASCII로 재작성하여 멀티바이트 파싱 문제 해결
  - `nohup` 호환성을 위한 `exec 2>/dev/tty` 제거
  - `SCRIPT_DIR/ROOT` 경로 해결 로직 강화 및 tmux/prompt injection 보안 강화
  - `.gitignore` 갱신: Claude Code 일반 상태는 무시하고 프로젝트 스킬(`solar-ralph`, `git-checkpoint`)은 추적 유지
  - `record-session.sh` 실행 권한 부여
  - **9개 항목 일관성 보정 (2026.07.20)**:
    - `commit-gate.sh`: 위치 인자(`$expected_p0`, `$rs_path`)를 환경변수(`os.environ`) 대신 argv로 전달하도록 Python 블록 3곳 수정; Gate 번호를 실행 순서(인덱스 폴루션=0, 승인경로검증=1, 비밀패턴검사=2, 작업트리신뢰도=3, 테스트증거=4, 스테이징=5, 스테이징후검증=6, 사전커밋검증=7, 커밋+JSON출력=8)에 맞게 재정렬
    - `preflight.sh`: 위치 기반 run-state 경로 전달(`sys.argv[1]`) 확인; 조건부 브랜치 우회 로직 없음 확인; `$# -lt 2` 옵션 가드 확인; 모든 출력이 stderr(`print -r -u2`)로 통일 확인
    - `SKILL.md`: Resume 섹션의 모순 문장("it may modify") 제거; 비수정 계약("never modifies worktree files or Git history - on success or on failure. No staging, committing, resetting, or file modification occurs as part of resume, regardless of outcome.") 명확화; "twice before" → "once already" 통일
    - `state-contract.md`: `P0 Item Schema`의 `status` 필드에 `needs-operator` 추가; Resume Consistency Contract (4개 독립 비교) 문서화; Status Transitions 표에 `tests_passed`, `checkpoint_failed`, `needs-operator` 포함; State Write Distinctions (원자적 교체 vs 추가 전용) 정리
  - **전체 히스토리 co-authored-by 제거 (2026.07.20)**: `git rebase -i --root`를 통해 과거 커밋 7개에 포함된 `Co-Authored-By: Claude...` 트레일러 제거, 히스토리 정리 완료
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
