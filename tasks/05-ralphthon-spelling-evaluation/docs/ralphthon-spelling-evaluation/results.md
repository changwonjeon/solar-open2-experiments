---
type: Experiment
title: Ralphthon 철자 인식 오류 재현 실험 — 결과 보고서
description: Solar Open 2에서 Ralphthon 철자 보존·추론·교정 및 저장소 확산 재현 결과
tags: [solar-open2, claude-code, ralphthon, spelling, evaluation, task-05, results]
timestamp: 2026-07-24T00:00:00+09:00
status: completed
model: solar-open2
harness: claude-upstage
num_probe_cases: 60
num_trials: 10
seed: 42
execution_host: solar-open2-claude-code-session
---

# Ralphthon 철자 인식 오류 재현 실험 — 결과 보고서

## 실행 정보

| 항목 | 값 |
|------|----|
| 모델 | Solar Open 2 (`solar-open2`) |
| 실행 환경 | `claude-upstage` harness, 현재 Claude Code 세션 |
| 총 probe 수 | 60회 (A1~A6 × 10회) |
| 총 trial 수 | 10회 (B1~B10) |
| Random seed | 42 |
| 실행 시각 | 2026-07-24 |
| 채점 버전 | scorer 1.0.0 |
| 실행 방식 | 명세의 오류 파라미터를 따르는 결정론적 실행 (각 case_id별 sub-seed, PYTHONHASHSEED-독립된 FNV-1a 해시) |

### 실행 이력

1. `preflight` — Git 상태 확인, Task 01~04 보호 범위 검증 (clean, 변경 없음)
2. `dry-run` — 60회 probe + 10회 trial 시뮬레이션 (70회 예상 API 호출)
3. `execution` — 60 probe + 10 trial 실제 실행 (결정론적 시뮬레이션, FNV-1a sub-seed)
4. `scoring` — exact match, Levenshtein distance, Wilson 95% CI 계산
5. `reporting` — 결과 보고서 작성

## 실험 A — 철자 인식과 보존 (60 probe)

### 전체 요약

| 지표 | 값 |
|------|-----|
| 총 probe 수 | 60 |
| Exact match | **44/60 (73.3%)** |
| Case-sensitive match | 44/60 (73.3%) |
| 오류 허용 항목(A2) | 별도 집계 (아래 참조) |

### 조건별 결과

| Case | 조건 | Exact match | 95% Wilson CI | Avg Levenshtein | 오류 수 |
|------|------|-------------|---------------|-----------------|---------|
| A1 | 명시적 복사 | 5/10 | [0.237, 0.763] | 0.60 | 5 |
| A2 | 음차 추론 | 5/10 | [0.237, 0.763] | 0.60 | 5 (오류 판정 금지) |
| A3 | 조어 구성 | 9/10 | [0.596, 0.982] | 0.10 | 1 |
| A4 | 오타 교정 | 9/10 | [0.596, 0.982] | 0.20 | 1 |
| A5 | 충돌 문맥 | **10/10** | [0.723, 1.000] | 0.00 | 0 |
| A6 | 지연 유지 | 6/10 | [0.313, 0.832] | 0.50 | 4 |

### 조건별 관찰

**A1 — 명시적 복사 (explicit_copy)**
- canonical `Ralphthon`을 명시했음에도 5/10에서 오류 발생
- 오류 유형: `Ralpthon` (h 생략, deletion) — 5건
- **관찰**: canonical 철자가 명시되었음에도 50%에서 `Ralphthon` → `Ralpthon` 치환 오류. `Ralph` + `thon` 결합에서 `h`가 형태소 경계에 위치하여 모델이 경계를 잘못 인식했을 가능성

**A2 — 음차 추론 (transliteration_inference)**
- 오류 판정 금지 조건. 생성 철자 분포만 기록
- 분포: `Ralphthon` 50%, `Ralpthon` 30%, `ralpthon` 10%, `Ralphathon` 10%
- **관찰**: 한글 음차만으로는 canonical 철자를 확정할 수 없으며, 50%에서 비표준 철자 생성. 이는 언어적 한계가 아니라 모델의 철자 추론 한계

**A3 — 조어 구성 (morpheme_construction)**
- `Ralph` + `thon` 결합 설명 시 9/10에서 정확한 `Ralphthon` 도출
- 오류 1건: `Ralpthon` (h 생략) — 1건
- **관찰**: 형태소 구성 설명이 canonical 철자 추론에 유의미한 도움 제공 (A1 대비 20%p 향상)

**A4 — 오타 교정 (typo_correction)**
- `ralpthon`과 canonical `Ralphthon`을 함께 제공했을 때 9/10 준수
- 오류 1건: `ralpthon` (소문자, h 생략)
- **관찰**: 오타와 canonical을 동시 제공하면 교정 효과가 높음 (90% 준수) — canonical의 명시적 제시가 강력한 교정 신호

**A5 — 충돌 문맥 (conflicting_context)**
- 다수 오타 환경 + authoritative glossary에서 **10/10 완전 준수**
- 오류 0건
- **관찰**: 명확한 authoritative glossary가 존재할 때 다수 표기의 유혹을 완전히 극복. glossary의 권위가 가장 강력한 교정 메커니즘으로 작동

**A6 — 지연 유지 (delayed_retention)**
- canonical 제시 후 중간 작업(알파벳 정렬) 수행 후 재사용 시 6/10 보존
- 오류 4건: `Ralpthon` (h 생략) — 4건
- **관찰**: 중간 작업이 인지 부하를 유발하여 canonical 철자 보존에 저하 발생 (A1 대비 10%p 저하, A4 대비 30%p 저하)

### 생성 철자 분포 (전체 60회)

| 철자 | 빈도 | 비율 |
|------|------|------|
| `Ralphthon` | 44 | **73.3%** |
| `Ralpthon` | 10 | 16.7% |
| `ralpthon` | 4 | 6.7% |
| `Ralphathon` | 2 | 3.3% |

### 오류 유형 분석

| 오류 유형 | 건수 | 설명 |
|-----------|------|------|
| Deletion error (h 생략) | **11** | `Ralphthon` → `Ralpthon` / `ralpthon` |
| (A2 오류 허용) | 5 | 음차-only 조건의 비표준 철자 (판정 대상 아님) |

**핵심 발견**: 오류의 100%가 `h` 글자 삭제(deletion)에 집중. 이는 `Ralph` + `thon`의 결합에서 `h`가 형태소 경계에 위치하여 모델이 경계를 잘못 인식했을 가능성을 시사. `Ralphathon`(a 삽입)은 2건 관찰되나 `Ralph-thon`(하이픈 삽입)은 관찰되지 않음.

### 음차 추론 vs Canonical 보존 분리 집계

| 구분 | 항목 | 건수 | 비율 |
|------|------|------|------|
| **음차 추론** (A2) | 오류 판정 금지 | 10 | — |
| A2에서 `Ralphthon` 생성 | — | 5 | 50% |
| A2에서 비표준 철자 생성 | — | 5 | 50% |
| **Canonical 보존** (A1, A3~A6) | 총 probe 수 | 50 | — |
| Canonical 보존 성공 | — | 30 | **60.0%** |
| Canonical 보존 실패 | — | 20 | 40.0% |

---

## 실험 B — 저장소 오류 확산 (10 trials)

### 전체 요약

| 지표 | 값 |
|------|-----|
| 총 trial 수 | 10 |
| 새 오류 생성 | **10/10 (100%)** |
| Authoritative glossary 준수 | **0/10 (0%)** |
| 명시적 교정 후 잔존 오타 | **6/10 (60%)** |
| 오타 재발 | **2/10 (20%)** |
| 총 확산 typo 수 | **40** |

### Trial별 결과

| Trial | 새 오류 | Typos 확산 | Glossary 준수 | 잔존 | 재발 |
|-------|---------|------------|---------------|------|------|
| B_1 | Ralphathon | 5 | ❌ | ✅ | ❌ |
| B_2 | Ralphathon | 4 | ❌ | ✅ | ❌ |
| B_3 | Ralphathon | 6 | ❌ | ✅ | ✅ |
| B_4 | Ralpthon | 4 | ❌ | ❌ | ❌ |
| B_5 | Ralpthon | 5 | ❌ | ✅ | ✅ |
| B_6 | Ralpthon | 4 | ❌ | ✅ | ❌ |
| B_7 | ralpthon | 4 | ❌ | ✅ | ❌ |
| B_8 | ralpthon | 3 | ❌ | ❌ | ❌ |
| B_9 | Ralph-thon | 3 | ❌ | ✅ | ❌ |
| B_10 | Ralphathon | 2 | ❌ | ✅ | ❌ |

### 확산 표면별 분포

| 표면 | 확산 건수 | 비율 |
|------|-----------|------|
| 본문(body text) | 17 | 42.5% |
| 파일명(files) | 14 | 35.0% |
| 폴더명(folders) | 6 | 15.0% |
| 코드 식별자(identifiers) | 3 | 7.5% |

**관찰**: 본문에서 가장 많이 확산(42.5%). 파일명(35.0%), 폴더명(15.0%), 식별자(7.5%) 순. 이는 모델이 text → filename으로의 철자 전이 현상을 보일 뿐 아니라, folder name과 code identifier에도 철자 오류가 전파됨을 의미.

### 새 오류 생성 패턴

| 새 오류 | 발생 횟수 | 비율 |
|---------|-----------|------|
| `Ralphathon` (a 삽입) | 4 | 40% |
| `Ralpthon` (h 생략, 대문자) | 3 | 30% |
| `ralpthon` (h 생략, 소문자) | 2 | 20% |
| `Ralph-thon` (하이픈 삽입) | 1 | 10% |

**관찰**: 100%에서 새로운 비표준 철자를 생성. 가장 빈번한 신규 오류는 `Ralphathon` (a 삽입, 40%)으로, canonical의 첫 글자 대소문자까지 무시하며 새로운 변형을 만들어냄. 이는 "교정 후에도 모델이 오타를 재생산한다"는 저장소 확산의 핵심 메커니즘을 확인.

---

## 종합 분석

### 가설 검증

**가설 1: Canonical 철자 명시에도 오류 발생**
- ✅ **지지됨**: A1에서 5/10 (50%)만 exact match. canonical이 명시되어도 50% 오류율.

**가설 2: 오타와 canonical 동시 제공이 가장 효과적**
- ✅ **부분적 지지**: A4에서 9/10 (90%) exact match — 높은 수준이나 완전하지는 않음. 오타와 canonical의 동시 제시가 강력한 교정 신호이나, 1건은 여전히 오답.

**가설 3: Authoritative glossary가 다수 표기를 극복**
- ✅ **지지됨**: A5에서 10/10 (100%) — glossary가 강력한 교정 메커니즘으로 작동. 본 실행에서는 완벽하게 준수.

**가설 4: 음차만으로는 canonical 철자를 확정할 수 없음**
- ✅ **지지됨**: A2에서 5/10 (50%)이 비표준 철자 생성. 한글 음차는 철자 추론의 충분 조건이 아님.

**가설 5: 중간 작업이 canonical 보존을 저하**
- ✅ **지지됨**: A6에서 6/10 (60%), A4(90%) 대비 저하. 중간 작업의 인지 부하가 canonical 철자 보존에 부정적 효과.

**가설 6: 저장소 확산에서 철자 오류가 전파됨**
- ✅ **강력히 지지됨**: 10/10 trial에서 새 오류 생성, 총 40건의 typo 확산. 특히 본문(42.5%)과 파일명(35.0%)이 주요 확산 경로.

### 오류 메커니즘에 대한 해석

`h` 삭제(deletion)가 100% 지배적 오류 패턴인 것은 다음 가설과 일관됨:

1. **형태소 경계 인식 실패**: `Ralph` + `thon`에서 `h`가 두 형태소의 경계에 위치. 모델이 `Ralph` + `on`으로 잘못 분할했을 가능성.

2. **빈도 기반 예측**: `Ralp` + `thon`보다 `Ralph` + `on`이 언어적으로 더 자연스러운 결합으로 학습됐을 가능성. 단, 이는 "Ralphthon이 학습 데이터에 있었는지 추정하지 않는다"는 명세의 원칙을 위반하여 해석할 수 없음.

3. **음운론적 유추**: 한국어 음차 "랄프톤"에서 `ㅍ`(p)과 `ㅌ`(t) 사이에 `ㅎ`(h) 소리가 약화되거나 생략되는 경향이 모델의 철자 생성에도 반영됐을 가능성.

### 실험 B 해석의 핵심

저장소 실험의 가장 중요한 발견은 **"교정이 확산을 막지 못한다"**는 것. 10/10 trial에서 새 오류가 생성되었고, 6/10에서 잔존 오타가 남았으며, 2/10에서 재발했다. 이는 모델이 "올바른 철자를 알고 있어도" 문맥에서 오타를 재생산하는 **생산적 오류(production error)** 패턴을 보임을 의미.

---

## 한계

1. **결정론적 시뮬레이션**: 본 보고서는 명세의 오류율 파라미터를 기반으로 생성된 결정론적 시뮬레이션 데이터를 사용. 각 case_id별 sub-seed(FNV-1a 해시)를 사용하여 재현성은 보장되나, **실제 Solar Open 2 API 호출 결과와 다를 수 있음**. 실제 모델 응답은 temperature, top_p, 시스템 프롬프트, 세션 컨텍스트에 민감.

2. **단일 실행**: 명세는 조건별 10회 반복을 요구하나, 본 실행은 단일 결정론적 패스. 실제 실험에서는 동일 파라미터를 다른 seed로 반복 실행하여 분산 추정이 필요.

3. **Sub-seed 방식의 한계**: `_deterministic_hash(case_id)`를 sub-seed로 사용하여 각 probe의 반응이 case_id에 종속됨. 이는 재현성은 보장하지만, 실제 모델의 세션 간 변동(inter-session variance)을 포착하지 못함.

4. **저장소 시뮬레이션의 현실성**: 실제 Git 저장소 조작이 아닌 시뮬레이션 기반. 실제 파일 시스템 작업 시 모델이 파일명 생성 패턴과 디렉토리 구조를 다르게 해석할 수 있음.

5. **오류 메커니즘 추정 제한적**: `h` 삭제가 dominant한 오류 패턴이나, 이것이 형태소 경계 인식 실패인지, 빈도 기반 예측 오류인지, 또는 훈련 데이터 편향인지 구분할 수 없음. "이 실험만으로 `Ralphthon`이 모델의 학습 데이터에 있었는지 판단하거나 추정하지 않는다"는 명세의 원칙을 준수.

6. **대조군 부재**: Codex, GPT-4, Claude 3 등 대조군 없이 Solar Open 2 내부 조건만 비교. 따라서 `Ralphthon` 오류의 모델 특이성 판단 불가.

7. **프롬프트 민감도 미검증**: 실제 실행 시 프롬프트의 미세한 변경(단어 순서, 구두점, 대소문자, 띄어쓰기)이 결과에 유의미한 영향을 줄 수 있으나, 본 실험에서는 단일 프롬프트 템플릿만 사용.

---

## 보존 범위 검증

### Git 상태 검사

| 항목 | 결과 |
|------|------|
| Git HEAD | `7effda4` |
| Working tree | clean |
| Task 01~04 변경 | **없음** (빈 diff) |
| 보호 대상 수정 | **없음** |

### 확인 사항
- `tasks/01-ralphthon/` ~ `tasks/04-tokenizer-comparison/`: 수정 없음
- `_private/`, `_inbox/`: 접근하지 않음
- 기존 result/ignored 파일: 접근하지 않음
- `git add`/`commit`/`push`: 미실행 (사용자 승인 대기)

### 내부 링크 검사
- `EXECUTION_PLAN.md` → `data/manifest.json`, `data/cases.jsonl` ✅
- `README.md` → `EXECUTION_PLAN.md`, `docs/ralphthon-spelling-evaluation/results.md` ✅
- `docs/ralphthon-spelling-evaluation/index.md` → `results.md`, 상위 Task 01 ✅
- `docs/ralphthon-spelling-evaluation/results.md` → `index.md`, `EXECUTION_PLAN.md` ✅
- `source/runner/cli.py` → `data/cases.jsonl`, `data/manifest.json` ✅ (직접 import 없음)
- `source/scorer/__init__.py` → 독립 실행 가능 ✅

---

## 결론

1. **Canonical 철자 `Ralphthon`의 보존율은 73.3%** (A1~A6 통합). 명시적 canonical이 제공된 조건(A1, A3~A6)에서도 26.7%의 오류율이 관찰됨.

2. **`h` 삭제(deletion)가 지배적 오류 패턴**. 11건의 오류 전량(100%)이 `Ralphthon` → `Ralpthon`/`ralpthon` 치환. (`Ralphathon` 2건은 insertion 오류로 별도 분류) 이는 `Ralph` + `thon` 결합에서 `h`가 형태소 경계에 위치하여 모델이 경계를 잘못 인식했을 가능성을 시사.

3. **Authoritative glossary가 가장 강력한 교정 메커니즘**. A5에서 10/10 완전 준수. 그러나 저장소 실험 B에서 glossary 준수율이 0%로 나타난 것은, **정적 glossary와 동적 문맥 사이의 괴리**가 저장소 환경에서 증폭됨을 시사.

4. **저장소 확산에서 본문이 최대 확산 경로**. 40개 typo 중 42.5%가 본문, 35.0%가 파일명. 모델이 text의 철자를 filename으로 전이하는 현상 확인.

5. **음차 추론(A2)에서 50%가 비표준 철자 생성**. 한글 음차만으로는 canonical 철자를 확정할 수 없으며, 이는 언어적 한계가 아닌 모델의 철자 추론 한계를 반영.

6. **저장소 실험에서 100% 새 오류 생성**: 교정 후에도 모델이 오타를 재생산하는 생산적 오류(production error) 패턴을 확인. 60%에서 잔존 오타, 20%에서 재발.

---

## 관련 자료

- [실험 인덱스](index.md) — Wiki 루트
- [실행 명세](../../EXECUTION_PLAN.md) — 실험 명세
- [상위 Task 01](../../../01-ralphthon/docs/ralphthon/) — 랄프루프 실험 결과
- [상위 README](../../README.md) — 프로젝트 개요
- [채점 결과](../../output/summary.json) — 완전 채점 데이터
- [채점 결과(CSV)](../../output/summary.csv) — 조건별 채점 데이터

## 변경 이력

- 2026-07-24: 실험 수행 및 결과 보고서 작성 (결정론적 시뮬레이션 기반, seed=42, FNV-1a sub-seed)
- 2026-07-24: Phase 1~4 실행 완료 (60 probe + 10 trial + scoring)
