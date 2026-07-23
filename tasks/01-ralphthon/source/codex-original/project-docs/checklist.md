---
type: Work Checklist
title: Ralphthon OKF 전환 체크리스트
description: 기존 행사 자료를 OKF v0.1 번들 구조로 정리하기 위한 작업 목록.
tags: [ralphthon, okf, migration]
timestamp: 2026-07-12T11:00:00+09:00
---

# Checklist

- [x] 기존 Markdown 파일과 작업트리 상태를 확인한다.
- [x] OKF 디렉터리 구조를 결정한다.
- [x] 기존 문서를 적절한 디렉터리로 이동한다.
- [x] 모든 개념 문서에 필수 `type` frontmatter를 추가한다.
- [x] 루트와 하위 디렉터리의 `index.md`를 작성한다.
- [x] 변경 이력을 `log.md`에 기록한다.
- [x] OKF 적합성, 내부 링크, 기존 내용 보존을 검증한다.

## Notion Participant Guide 수집

- [x] 입력 PDF와 ZIP의 파일 형식 및 구성을 확인한다.
- [x] PDF 전 페이지를 렌더링하고 원문 내용을 확인한다.
- [x] ZIP 첨부파일을 안전하게 추출하고 누락 여부를 확인한다.
- [x] 원본과 정리된 참가자 가이드를 OKF 구조에 배치한다.
- [x] 인덱스, 변경 로그, 컨텍스트 노트를 갱신한다.
- [x] OKF 메타데이터, 내부 링크, 첨부파일을 검증한다.

## Track 2 계획안 현실화

- [ ] 원본 계획 패키지와 공식 Track 2 템플릿을 대조한다.
- [ ] 원본 ZIP을 보존하고 수정 작업용 패키지를 추출한다.
- [ ] README와 구현 로드맵을 25분·10편 제약에 맞게 개정한다.
- [ ] Codex 지시문에 OpenAgentReview 실행 경로와 제출 계약을 반영한다.
- [ ] Technical Report, Title, Abstract와 리뷰 결과물 체크리스트를 추가한다.
- [ ] 수정 패키지의 문서 일관성, 링크, ZIP 무결성을 검증한다.

## Track 2 Codex Skill 제작 계획

- [x] 25분·10편 기준의 목표와 성공 조건을 정의한다.
- [x] Root Coordinator와 Review Worker 3개의 병렬 구조를 설계한다.
- [x] 플랫폼 부작용의 단일 소유권과 실패 복구 상태를 정의한다.
- [x] BUILD, DRY-RUN, LIVE 모드와 리뷰 출력 계약을 정의한다.
- [x] 50분 구현 일정과 검증·Go/No-Go 기준을 작성한다.
- [x] 오전 Spec부터 Ralph Loop, Human Editing, 제출, live review까지 전체 실행 명세로 확장한다.
- [x] 무인 반복 계약, checkpoint, failure ledger, feature freeze, handoff를 정의한다.
- [x] OpenAgentReview 로그인과 기본 세션 확인을 완료한다.
- [ ] 행사 venue가 공개된 뒤 논문 목록·PDF의 read-only smoke test를 완료한다.
- [x] tmux 기반 OMX Ralph 실행 표면을 확정하고 tmux에서 Codex·OMX smoke test를 통과한다.
- [x] 작업폴더 Git baseline을 private 원격에 push한다.
- [x] Ralph Goal과 context snapshot hash를 동결한다.
- [x] Mac 전원 연결을 확인한다.
- [x] `caffeinate` launcher와 Tectonic PDF 생성 경로를 확인한다.
- [ ] 12:30에 Ralph Loop를 시작해 Skill과 제출자료 구현을 실행한다.
- [x] GitHub 루트 `README.md`의 pre-Ralph 버전을 작성한다.
- [ ] Ralph가 루트 `README.md`를 실제 검증 결과와 동기화한다.
