---
type: Guide
title: HuggingFace 계정 기반 모델 다운로드 가이드
description: 토크나이저 비교에 필요한 HuggingFace 모델 접근과 다운로드 안내
---

# HuggingFace 계정 기반 모델 다운로드 가이드

이 데모의 7개 모델은 HuggingFace에서 공개 라이선스로 배포되어 계정 없이 다운로드 가능합니다.
하지만 **Llama-4 Maverick 17B**와 **Gemma-4 31B-IT**는 추가 접근이 필요합니다.

---

## 1. Llama-4 Maverick 17B (meta-llama/Llama-4-Maverick-17B-128E-Instruct)

### ⚠️ 접근 요구사항
- **HuggingFace 계정 필수** (무료 가입 가능)
- **Meta의 gated 모델**로, 승인 과정이 필요할 수 있음
- 모델 카드: https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct

### 다운로드 방법 (계정 승인 후)

```bash
# 1. HuggingFace 로그인
huggingface-cli login
# 또는 환경변수로:
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx

# 2. 토크나이저만 다운로드 (모델 가중치는 불필요)
python -c "
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained('meta-llama/Llama-4-Maverick-17B-128E-Instruct')
tok.save_pretrained('/path/to/tasks/04-tokenizer-comparison/source/original/models/meta-llama-Llama-4-Maverick')
"

# 3. 이미 로컬에 저장된 토크나이저를 데모를 재실행하면 자동으로 감지됨
```

### 계정 생성 및 모델 승인 절차
1. https://huggingface.co/join 에서 무료 계정 생성
2. https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct 접속
3. "Access repository" 버튼 클릭 → 동의 조건 확인
4. 승인 대기 (보통 즉시 또는 몇 시간 내)
5. `huggingface-cli login`으로 토큰 발급 (Settings → Access Tokens)

### 대안: 데모에서 Llama-4를 언급하지 않는 방법
강연장에서 HF 계정 설정이 어렵다면, 현재 7개 모델(업스테이지, LG AI, Qwen, Zhipu, Moonshot, Google)로도 충분히 인상적인 비교가 가능합니다.

---

## 2. Gemma-4 31B-IT (google/gemma-4-31B-it)

### ✅ 접근 요구사항
- **HuggingFace 계정 필요** (일반적으로)
- **Apache-2.0 라이선스** (개방적)
- 모델 카드: https://huggingface.co/google/gemma-4-31B-it

### 다운로드 방법

```bash
# 방법 1: HF CLI
huggingface-cli login
python -c "
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained('google/gemma-4-31B-it')
tok.save_pretrained('/path/to/demos/tokenizer-comparison/models/google-gemma-4-31B-it')
"

# 방법 2: 이미 이 데모에 포함되어 있음!
# 구글 모델은 이미 로컬에 저장되어 있으므로 추가 작업 불필요
```

> **참고**: 이 데모에서는 이미 `google-gemma-4-31B-it`의 토크나이저가 로컬에 다운로드되어 있습니다.
> 추가 다운로드가 필요한 경우 위 명령어를 사용하세요.

---

## 3. 토크나이저 파일만 다운로드하는 이유

이 데모는 **모델의 가중치를 사용하지 않습니다**. 오직 tokenizer.json, vocab, merges 등 토큰화 규칙만 필요합니다.

- **토크나이저 파일 크기**: 약 12~31MB (모델 가중치의 0.01% 수준)
- **다운로드 시간**: 수 초 ~ 수십 초 (모델 가중치는 수 GB ~ 수십 GB)
- **오프라인 사용**: 토크나이저만 있으면 인터넷 없이 토큰화 가능

---

## 4. 데모에 Llama-4/Gemma-4를 추가하는 방법

1. HuggingFace 계정 생성 및 로그인
2. 해당 모델 페이지에서 접근 승인
3. 위 다운로드 명령어 실행
4. 토크나이저가 `demos/tokenizer-comparison/models/`에 저장됨
5. `app.py` 하단의 주석 처리된 Llama-4 항목을 활성화

```python
# app.py의 MODELS 딕셔너리에 추가:
"meta-llama-Llama-4-Maverick": {
    "display_name": "Llama-4 Maverick 17B",
    "vendor": "Meta",
    "repo": "https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct",
    "official_model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
    "color": "#E74C3C",
},
```
