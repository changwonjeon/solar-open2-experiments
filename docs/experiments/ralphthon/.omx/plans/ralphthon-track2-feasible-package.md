---
type: Work Plan
title: Ralphthon Track 2 현실 실행 패키지 개정 계획
description: 기존 v3를 10편·25분 및 제출물 중심의 v4 패키지로 전환하는 작업 계획.
tags: [ralphthon, track-2, plan]
timestamp: 2026-07-12T11:30:00+09:00
---

# Requirements Summary

- 원본 ZIP은 변경하지 않고 보존한다.
- Critic–Verifier 핵심 아이디어를 유지한다.
- OpenAgentReview claim-read-review-post와 10편·25분 제약을 MVP의 중심으로 둔다.
- Technical Report, Title, Abstract와 리뷰 결과를 함께 고려한다.

# Acceptance Criteria

- v4 로드맵과 Codex 지시문의 우선순위가 일치한다.
- 공식 리뷰 필드와 점수 범위가 모두 명시된다.
- mock 10편 24분, 논문별 120초, 중복 post 0건을 검증 기준으로 갖는다.
- 4페이지 Technical Report 구성과 제출 체크리스트가 있다.
- 수정 ZIP 무결성 검사를 통과한다.

# Implementation Steps

1. 원본 ZIP과 공식 가이드를 대조한다.
2. v3를 보존하고 v4 event MVP를 추가한다.
3. README와 Codex 지시문이 v4를 우선하도록 수정한다.
4. 제출 계약과 Technical Report 구성을 추가한다.
5. 문서 간 계약과 패키지 무결성을 검증한다.

# Risks and Mitigations

- 실제 플랫폼 계약 미확정은 mock adapter로 숨기지 않고 blocker로 표시한다.
- 품질 기능이 처리량을 해치면 P0/P1 이후 기능을 중단한다.
- 공식 자료 간 차이는 당일 UI와 Notion 가이드를 우선한다.

# Verification

- Markdown frontmatter와 로컬 링크 검사.
- 필수 리뷰 필드 문자열 검사.
- 수정 ZIP `unzip -t`.
- manifest와 실제 파일 목록 비교.
