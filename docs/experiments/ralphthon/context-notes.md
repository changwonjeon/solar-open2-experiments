---
type: Context Notes
title: Ralphthon 작업 컨텍스트
description: Track 2 Review Agent 준비 과정의 결정과 근거를 누적 기록한다.
tags: [ralphthon, track-2, review-agent, okf]
timestamp: 2026-07-12T11:00:00+09:00
---

# Current Context

- 행사는 Auto Research를 주제로 한 Ralphthon Seoul 에디션이다.
- 참가 트랙은 Track 2 Review Agent다.
- 현재는 11:00–12:30 Research Specification 구간이다.
- Ralph Loop는 12:30–15:30이며 시작 후 에이전트 직접 조작이 제한된다.
- Track 2는 무작위 배정된 논문 10편을 제한 시간 안에 모두 리뷰해야 한다.
- 일정표상 실행 구간은 16:35–17:00이므로 설계상 25분을 보수적 시간 제한으로 사용한다.

# Decisions

## 2026-07-12 — OKF v0.1 채택

모든 작업 자료와 문서 구조는 Google Open Knowledge Format v0.1을 따른다. 일반 문서는 YAML frontmatter와 필수 `type`을 가지며, 디렉터리별 `index.md`를 통해 점진적으로 탐색한다.

## 2026-07-12 — 기존 파일명 보존

날짜 접두사는 자료의 생성 시점과 출처 맥락을 나타내므로 기존 파일명을 유지한다. 행사 원본 안내는 `event/`, 당일 세션 기록은 `sessions/`, 작업 관리 문서는 `work/`에 둔다.

## 2026-07-12 — 원문 최소 변경

기존 문서 본문은 수정하지 않고 OKF 적합성에 필요한 frontmatter만 보완한다. 구조 변경 이력은 루트 `log.md`에 기록한다.

## 2026-07-12 — OKF 전환 검증

전체 Markdown 12개 중 예약 문서 5개를 제외한 개념 문서 7개에 parse 가능한 YAML frontmatter와 비어 있지 않은 `type`이 있음을 확인했다. 모든 로컬 Markdown 링크의 대상도 존재한다.

## 2026-07-12 — Notion 참가자 가이드 입력 확보

Notion 웹페이지를 직접 읽을 수 없어 사용자가 PDF 내보내기 파일과 첨부파일 ZIP을 제공했다. PDF를 기준 원문으로 취급하고 ZIP의 파일을 함께 보존한 뒤, 별도의 OKF 참가자 가이드를 작성한다.

## 2026-07-12 — Notion 참가자 가이드 검증

PDF 6페이지를 PNG로 렌더링해 전 페이지를 시각적으로 확인하고 텍스트 전사본을 작성했다. 원본 PDF와 ZIP의 작업폴더 복사본은 각각 입력 파일과 바이트 단위로 동일하다. ZIP 무결성 검사를 통과했으며 9개 첨부파일이 모두 추출되었다. 전체 OKF 검사는 Markdown 19개, 개념 문서 9개, 깨진 로컬 링크 0개로 통과했다.

PDF SHA-256은 `8d5021163643bfff3c9f558f4b15d539fae9c489c01e96d32f8c89bd2e5126d4`이며 ZIP SHA-256은 `8b29290f5828e176debb57ea9cc00252502973d55ea561a2f18a7f0a326bfc6c`이다.

## 2026-07-12 — Track 2 계획안 현실화 기준

사용자가 제공한 계획안은 Critic–Verifier 분리와 provenance 측면에서는 강하지만, 행사 운영상 가장 중요한 OpenAgentReview의 login → browse → claim → PDF read → review post 경로와 10편·25분 처리량이 MVP에 포함되지 않았다. 수정본은 제출 성공을 최우선으로 하고 논문당 평균 150초, 개별 timeout, 실패 격리, 공식 리뷰 필드 완전성을 필수 게이트로 삼는다.

공식 `team-attention/ralphthon-icml` 저장소의 Track 2 자료는 `review-agent.md`와 구조화된 리뷰 결과를 별도 산출물로 동결하고, 논문·에이전트 버전과 hash, evidence trace를 기록하도록 안내한다. 다만 행사 당일 Notion 가이드의 Technical Report PDF, Title, Abstract 및 OpenAgentReview 제출 규정을 최종 운영 계약으로 우선한다.

## 2026-07-12 — Skill 제작은 계획 우선

사용자 요청에 따라 현재 단계에서는 `.codex/skills`와 `.codex/agents`를 생성하지 않는다. 먼저 25분 동안 10편을 처리할 Root Coordinator 1개와 Review Worker 3개의 구조, 직렬 플랫폼 lane, 결정론적 validator, 실패 복구, 제출물, 50분 구현 일정을 계획으로 확정한다. 계획 검토 뒤 Skill 구현을 별도 단계로 시작한다.

## 2026-07-12 — 주최측 추가 공식 링크 반영

오전 11:38에 공지된 공식 Skills 저장소, VESSL 크레딧, 오전 세션 슬라이드, Luma 행사 페이지를 추가 기준 자료로 등록한다. 공식 저장소는 `auto-research` Skill 안에 Track 2-only 경로와 `review-agent.md`·구조화 리뷰 템플릿을 제공한다. 따라서 자체 Skill은 이를 대체하지 않고 upstream commit과 hash를 고정한 뒤 10편·25분 병렬 orchestration을 확장한다. 공식 안내상 Track 2-only에는 GPU, VESSL, W&B, 새 실험이 필요하지 않다.

## 2026-07-12 11:56 — 오전 Spec과 오후 Ralph Loop 분리

11:00–12:30은 Skill 구현 시간이 아니라 전체 실행 spec을 동결하는 시간이다. 실제 Skill과 제출자료 제작은 12:30–15:30 Ralph Loop가 사용자 입력 없이 수행한다. 15:30–16:30에는 사람이 결과를 편집·제출하고, 16:35–17:00에는 완성된 Review Agent가 실제 배정 논문을 처리한다.

사전 점검 결과 Codex와 OMX는 동작하지만 tmux가 설치되어 있지 않아 OMX `$ralph` 지속 runtime은 즉시 사용할 수 없다. OpenAgentReview 로그인·세션·실제 adapter도 미확인이다. Git baseline, Ralph launch smoke test, OpenAgentReview read-only smoke test, 전원·잠자기 방지, PDF 생성 경로를 12:30 전 필수 gate로 둔다.

## 2026-07-12 12:04 — 사용자 사전 설정 확인

사용자가 `openagentreview.org` 로그인 완료 화면을 제공했고 Mac 전원이 연결되어 있음을 확인했다. 로그인 계정 메뉴가 표시되므로 기본 인증과 세션은 정상이다. 화면에는 active venue와 open submission venue가 아직 없으므로 행사 venue가 공개된 뒤 논문 목록과 PDF 접근만 추가 확인한다. 실제 claim과 post는 16:35 전 production에서 시도하지 않는다.

## 2026-07-12 12:15 — Ralph prelaunch 동결

tmux 3.7b와 Tectonic 0.16.9를 설치했다. tmux에서 Codex·OMX doctor를 실행했고 Tectonic으로 공식 ICML 예제 TeX를 7페이지 PDF로 빌드했다. Ralph context snapshot, `RALPH_GOAL.md`, guarded launcher, deadline watcher, checkpoint, failure ledger, handoff, root README와 SHA-256 manifest를 생성했다.

실제 `omx ralph` 실행 권한은 사용자에게 있다. 행사 진행에 맞춘 사용자의 명시적인 시작 신호 전에는 launcher, caffeinate keeper, deadline watcher를 실행하지 않는다.
