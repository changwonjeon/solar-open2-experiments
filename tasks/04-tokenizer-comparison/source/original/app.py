"""
LLM 토크나이저 비교 데모
 - HuggingFace open-weight 모델 (Solar 제외) + GPT계열(tiktoken) 토크나이저 비교
 - 한글/영어 텍스트 입력 시 토큰 수 및 토큰 분할 방식 시각화
 - 오프라인 지원: 모든 토크나이저 로컬에 저장됨 (HuggingFace/OpenAI 계정 불필요)
"""
import os
from typing import Optional

import streamlit as st
import tiktoken
from transformers import AutoTokenizer

# ═══════════════════════════════════════════════════════════════════
# 1. 모델 메타데이터
#    - Solar Open2 제거
#    - GPT: gpt-4o, gpt-4, gpt-3.5-turbo 3개만 유지
# ═══════════════════════════════════════════════════════════════════

OPEN_WHEIGHT_MODELS = {
    "LGAI-EXAONE-K-EXAONE-236B-A23B": {
        "display_name": "K-EXAONE 236B",
        "full_name": "K-EXAONE 236B-A23B",
        "vendor": "LG AI Research",
        "repo": "https://huggingface.co/LGAI-EXAONE/K-EXAONE-236B-A23B",
        "official_model": "LGAI-EXAONE/K-EXAONE-236B-A23B",
        "category": "Korean↔Open",
        "color": "#4ECDC4",
        "status": "✅ 로컬 저장 완료",
        "type": "hf",
    },
    "LGAI-EXAONE-EXAONE-4.5-33B": {
        "display_name": "EXAONE 4.5 33B",
        "full_name": "EXAONE 4.5 33B",
        "vendor": "LG AI Research",
        "repo": "https://huggingface.co/LGAI-EXAONE/EXAONE-4.5-33B",
        "official_model": "LGAI-EXAONE/EXAONE-4.5-33B",
        "category": "Korean↔Open",
        "color": "#45B7D1",
        "status": "✅ 로컬 저장 완료",
        "type": "hf",
    },
    "Qwen-Qwen3.6-35B-A3B": {
        "display_name": "Qwen3.6 35B-A3B",
        "full_name": "Qwen3.6 35B-A3B (MoE)",
        "vendor": "Alibaba / Qwen",
        "repo": "https://huggingface.co/Qwen/Qwen3.6-35B-A3B",
        "official_model": "Qwen/Qwen3.6-35B-A3B",
        "category": "Global↔Open",
        "color": "#7B68EE",
        "status": "✅ 로컬 저장 완료",
        "type": "hf",
    },
    "zai-org-GLM-5.2": {
        "display_name": "GLM-5.2",
        "full_name": "GLM-5.2 (Zhipu AI)",
        "vendor": "Zhipu AI",
        "repo": "https://huggingface.co/zai-org/GLM-5.2",
        "official_model": "zai-org/GLM-5.2",
        "category": "Global↔Open",
        "color": "#2ECC71",
        "status": "✅ 로컬 저장 완료",
        "type": "hf",
    },
    "moonshotai-Kimi-K2.5": {
        "display_name": "Kimi K2.5",
        "full_name": "Kimi K2.5 (Moonshot AI)",
        "vendor": "Moonshot AI",
        "repo": "https://huggingface.co/moonshotai/Kimi-K2.5",
        "official_model": "moonshotai/Kimi-K2.5",
        "category": "Global↔Open",
        "color": "#9B59B6",
        "status": "✅ 로컬 저장 완료",
        "type": "hf",
    },
    "google-gemma-4-31B-it": {
        "display_name": "Gemma 4 31B-IT",
        "full_name": "Gemma 4 31B-IT",
        "vendor": "Google",
        "repo": "https://huggingface.co/google/gemma-4-31B-it",
        "official_model": "google/gemma-4-31B-it",
        "category": "Global↔Open",
        "color": "#F39C12",
        "status": "✅ 로컬 저장 완료",
        "type": "hf",
    },
}

GPT_FAMILY_MODELS = {
    "gpt-4o": {
        "display_name": "GPT-4o",
        "full_name": "GPT-4 Omni",
        "vendor": "OpenAI",
        "repo": "https://openai.com/index/gpt-4/",
        "official_model": "gpt-4o",
        "category": "Global↔Proprietary",
        "color": "#00A2FF",
        "status": "✅ tiktoken 내장",
        "type": "tiktoken",
        "tiktoken_name": "o200k_base",
    },
    "gpt-4": {
        "display_name": "GPT-4",
        "full_name": "GPT-4 (8K/32K)",
        "vendor": "OpenAI",
        "repo": "https://openai.com/index/gpt-4/",
        "official_model": "gpt-4",
        "category": "Global↔Proprietary",
        "color": "#0066CC",
        "status": "✅ tiktoken 내장",
        "type": "tiktoken",
        "tiktoken_name": "o200k_base",
    },
    "gpt-3.5-turbo": {
        "display_name": "GPT-3.5 Turbo",
        "full_name": "GPT-3.5 Turbo",
        "vendor": "OpenAI",
        "repo": "https://openai.com/index/gpt-3-5/",
        "official_model": "gpt-3.5-turbo",
        "category": "Global↔Proprietary",
        "color": "#004BB5",
        "status": "✅ tiktoken 내장",
        "type": "tiktoken",
        "tiktoken_name": "cl100k_base",
    },
    "gpt-2": {
        "display_name": "GPT-2",
        "full_name": "GPT-2 (124M)",
        "vendor": "OpenAI",
        "repo": "https://openai.com/blog/gpt-2-150m/",
        "official_model": "gpt-2",
        "category": "Global↔Open",
        "color": "#5D6D7E",
        "status": "✅ tiktoken 내장",
        "type": "tiktoken",
        "tiktoken_name": "gpt2",
    },
}

# ═══════════════════════════════════════════════════════════════════
# 1b. GATED MODELS (대기 중인 gated 모델 — HF 승인 후 자동 활성화)
#    - Llama-3.1: Meta 승인 완료 — HF_TOKEN으로 접근 가능
# ═══════════════════════════════════════════════════════════════════
GATED_MODELS = {
    "meta-llama-Llama-3.1-8B-Instruct": {
        "display_name": "Llama-3.1 8B Instruct",
        "full_name": "Meta Llama-3.1 8B Instruct (Gated)",
        "vendor": "Meta",
        "repo": "https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct",
        "official_model": "meta-llama/Llama-3.1-8B-Instruct",
        "category": "Global↔Gated",
        "color": "#E74C3C",
        "status": "✅ 로컬 저장 완료",
        "type": "hf_gated",
        "hf_model_id": "meta-llama/Llama-3.1-8B-Instruct",
        "vocab_size": 128256,
    },
}

ALL_MODELS = {
    **OPEN_WHEIGHT_MODELS,
    **GPT_FAMILY_MODELS,
    **GATED_MODELS,
}

BASE_MODEL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models",
)


# ═══════════════════════════════════════════════════════════════════
# 2. 토크나이저 캐싱
# ═══════════════════════════════════════════════════════════════════

@st.cache_resource
def load_hf_tokenizer(model_key: str, info: dict | None = None) -> Optional[AutoTokenizer]:
    """HuggingFace 토크나이저를 로드 (캐싱됨)"""
    if model_key in GPT_FAMILY_MODELS:
        return None

    # 먼저 로컬 디렉토리에 토크나이저가 있는지 확인 (gated 여부와 무관)
    model_dir = os.path.join(BASE_MODEL_DIR, model_key)
    if os.path.isdir(model_dir) and os.path.isfile(os.path.join(model_dir, "tokenizer.json")):
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_dir, use_fast=True, local_files_only=True
            )
            return tokenizer
        except Exception:
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    model_dir, use_fast=False, local_files_only=True
                )
                return tokenizer
            except Exception:
                pass

    # 로컬에 없으면 gated 모델은 HF Hub에서 다운로드 시도
    if info and info.get("type") == "hf_gated":
        hf_model_id = info.get("hf_model_id")
        if hf_model_id:
            try:
                # Load HF_TOKEN from environment or .env file
                hf_token = os.environ.get("HF_TOKEN", "")
                if not hf_token:
                    env_path = os.path.join(os.path.dirname(__file__), ".env")
                    if os.path.isfile(env_path):
                        with open(env_path, "r", encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                if line.startswith("HF_TOKEN="):
                                    hf_token = line.split("=", 1)[1].strip()
                                    break
                if hf_token:
                    tokenizer = AutoTokenizer.from_pretrained(
                        hf_model_id,
                        use_fast=True,
                        token=hf_token,
                    )
                    return tokenizer
            except Exception:
                pass

    return None


@st.cache_resource
def get_tiktoken_encoder(model_key: str):
    """GPT 계열 모델의 tiktoken 인코더를 가져옴"""
    if model_key not in GPT_FAMILY_MODELS:
        return None
    model_info = GPT_FAMILY_MODELS[model_key]
    tiktoken_name = model_info.get("tiktoken_name")
    if not tiktoken_name:
        return None
    try:
        return tiktoken.get_encoding(tiktoken_name)
    except Exception:
        return None


def load_model_tokenizer(model_key: str):
    """
    모델 키에 따라 적절한 토크나이저를 로드
    - HF 모델: AutoTokenizer 로드
    - GPT 계열: tiktoken 인코더 로드
    """
    if model_key in GPT_FAMILY_MODELS:
        return get_tiktoken_encoder(model_key)
    else:
        return load_hf_tokenizer(model_key)


# ═══════════════════════════════════════════════════════════════════
# 3. 샘플 텍스트
# ═══════════════════════════════════════════════════════════════════

SAMPLE_TEXTS = {
    "한글_예시1": "인공지능은 우리의 삶을 근본적으로 바꾸고 있으며, 딥러닝과 머신러닝의 눈부신 발전으로 자연어 처리 기술이 비약적으로 향상되었다. 특히 언어 모델의 성능이 크게 개선되어 다양한 응용 분야에서 활용되고 있다.",
    "한글_예시2": "최근의 언어 모델은 방대한 양의 텍스트 데이터를 학습하여 문맥을 이해하고, 새로운 텍스트를 생성할 수 있는 능력을 갖추었다. 이러한 발전은 번역, 요약, 질문 응답 등 다양한 자연어 처리 작업에 혁신을 가져왔다.",
    "한영_혼합": "GenAI technologies like GPT, Claude, and Gemini have revolutionized natural language processing. 한국어 처리는 Solar와 EXAONE이 강점을 보이며, 특히 형태소 분석과 문맥 이해에서 뛰어난 성능을 발휘한다. The rapid advancement of transformer architectures has enabled models to achieve human-level performance on many benchmarks.",
    "기술_예시": "토크나이제이션은 BPE, WordPiece, SentencePiece 등의 알고리즘을 사용하여 텍스트를 토큰 단위로 분할한다. 이 과정은 언어 모델의 성능과 효율성에 직접적인 영향을 미치며, 특히 한국어의 경우 자소, 바이트, 형태소 등 다양한 단위로 분할되는 방식이 모델마다 크게 다르다.",
    "긴_한글": "Language models have transformed the landscape of natural language processing. From rule-based systems to statistical methods and now deep learning approaches, the evolution has been remarkable. 한국어 처리 기술은 특히 형태소 분석, 구문 분석, 의미 분석 등에서 꾸준한 발전을 이루어 왔다. 최근의 대규모 언어 모델은 수천억 개의 파라미터를 갖추고 있어 복잡한 언어 현상을 높은 정확도로 처리할 수 있다. 이러한 모델은 다양한 언어로 학습되어 다국어 지원이 가능하며, 특히 한국어의 복잡한 문법 구조를 이해하는 데 강점을 보인다. The integration of attention mechanisms and transformer architectures has been a game-changer, enabling models to capture long-range dependencies in text.",
}


# ═══════════════════════════════════════════════════════════════════
# 4. 토크나이즈 함수
# ═══════════════════════════════════════════════════════════════════

def tokenize_hf(tokenizer, text: str) -> list[tuple[str, int, int]]:
    """
    HuggingFace 토크나이저로 텍스트 토큰화
    Returns: list of (token_string, start_offset, end_offset)
    """
    try:
        encoding = tokenizer(text, return_offsets_mapping=True)
        result = []
        for token_id, (start, end) in zip(encoding.input_ids, encoding.offset_mapping):
            if start == 0 and end == 0:
                continue  # special tokens (CLS, SEP, PAD 등)
            token_str = text[start:end]
            result.append((token_str, start, end))
        return result
    except Exception:
        try:
            encoding = tokenizer(text, add_special_tokens=False)
            tokens = tokenizer.convert_ids_to_tokens(encoding.input_ids)
            if not tokens:
                return _tokenize_bytes_fallback(text)
            result = []
            pos = 0
            for token in tokens:
                if token.startswith("▁"):
                    token_str = " " + token[1:]
                elif isinstance(token, bytes):
                    try:
                        token_str = token.decode("utf-8")
                    except UnicodeDecodeError:
                        token_str = token.decode("utf-8", errors="replace")
                else:
                    token_str = str(token)
                token_str = token_str.replace("▁", " ")
                idx = text.find(token_str, pos)
                if idx != -1:
                    result.append((token_str, idx, idx + len(token_str)))
                    pos = idx + len(token_str)
                else:
                    result.append((token_str, pos, pos + len(token_str)))
                    pos += len(token_str)
            return result
        except Exception:
            return _tokenize_bytes_fallback(text)


def _tokenize_bytes_fallback(text: str) -> list[tuple[str, int, int]]:
    """바이트 단위 fallback 토큰화"""
    result = []
    pos = 0
    encoded = text.encode("utf-8")
    for i, byte in enumerate(encoded):
        char = chr(byte)
        start = pos
        end = pos + 1
        result.append((char, start, end))
        pos = end
    return result


def tokenize_tiktoken(encoder, text: str) -> list[tuple[str, int, int]]:
    """
    tiktoken으로 GPT 계열 모델 토큰화
    Returns: list of (token_string, start_offset, end_offset)
    """
    try:
        token_ids = encoder.encode(text)
        tokens = []
        pos = 0
        for token_id in token_ids:
            try:
                token_bytes = encoder.decode_single_token_bytes(token_id)
                token_str = token_bytes.decode("utf-8", errors="replace")
            except Exception:
                token_str = f"[{token_id}]"
            idx = text.find(token_str, pos)
            if idx != -1:
                end = idx + len(token_str)
                tokens.append((token_str, idx, end))
                pos = end
            else:
                tokens.append((token_str, pos, pos + len(token_str)))
                pos += len(token_str)
        return tokens
    except Exception:
        return _tokenize_bytes_fallback(text)


# ═══════════════════════════════════════════════════════════════════
# 4b. ETRI-style morphological analysis + full dict return functions
# ═══════════════════════════════════════════════════════════════════

def tokenize_hf_with_analysis(tokenizer, text: str, model_key: str) -> dict:
    """
    HuggingFace 토크나이저로 텍스트 토큰화하고 ETRI 형태소 분석 결과 포함
    Returns: dict with keys:
        - tokens: list of (token_string, start_offset, end_offset)
        - elt_output: ETRI 형태소 분석 결과 문자열 (한글 텍스트인 경우)
        - elt_morphs: ETRI 형태소 분석 결과의 형태소 리스트 (한글 텍스트인 경우)
        - lang_type: 텍스트 언어 유형 ('korean', 'english', 'mixed', 'other')
        - byte_count: 비-한글 문자의 바이트 수
    """
    tokens = tokenize_hf(tokenizer, text)

    lang_type = get_lang_type(text)

    # ETRI 형태소 분석 (한글 텍스트인 경우)
    elt_output = None
    elt_morphs = None
    if lang_type in ('korean', 'mixed'):
        # 한국어 형태소 분석 — 규칙 기반 형태소 분해
        # (ETRI 라이브러리 대체: 한글 음절 단위로 단순 분할 후 CC/NNG/VV 등 POS 할당)
        elt_morphs = _simple_korean_morphs(text)
        if elt_morphs:
            # get_elt_tags를 사용하여 EC/CF 및 EF 태그 보정
            elt_tags = get_elt_tags(elt_morphs)
            elt_output = "\n".join(f"{m[0]:4s}/{m[1]}" for m in elt_tags)
            # elt_morphs를 태그 보정된 형태로 업데이트
            for i, (m_text, m_tag) in enumerate(elt_tags):
                if i < len(elt_morphs):
                    elt_morphs[i]['text'] = m_text
                    elt_morphs[i]['type'] = m_tag

    # 비-한글 문자의 바이트 수 계산 (byte-level splitting 확인용)
    byte_count = 0
    for c in text:
        if c.isascii() and c.isalpha():
            byte_count += 1
        elif not ('가' <= c <= '힣'):
            byte_count += len(c.encode('utf-8'))

    return {
        'tokens': tokens,
        'elt_output': elt_output,
        'elt_morphs': elt_morphs,
        'lang_type': lang_type,
        'byte_count': byte_count,
    }


def tokenize_tiktoken_with_analysis(encoder, text: str) -> dict:
    """
    tiktoken으로 GPT 계열 모델 토큰화하고 분석 결과 포함
    Returns: dict with keys:
        - tokens: list of (token_string, start_offset, end_offset)
        - elt_output: None (GPT 계열은 ETRI 분석 미지원)
        - elt_morphs: None
        - lang_type: 텍스트 언어 유형
        - byte_count: 비-한글 문자의 바이트 수
    """
    tokens = tokenize_tiktoken(encoder, text)
    lang_type = get_lang_type(text)

    # 비-한글 문자의 바이트 수 계산
    byte_count = 0
    for c in text:
        if c.isascii() and c.isalpha():
            byte_count += 1
        elif not ('가' <= c <= '힣'):
            byte_count += len(c.encode('utf-8'))

    return {
        'tokens': tokens,
        'elt_output': None,
        'elt_morphs': None,
        'lang_type': lang_type,
        'byte_count': byte_count,
    }


def _simple_korean_morphs(text: str) -> list[dict[str, str | int]]:
    """
    한글 텍스트에 대한 간단한 규칙 기반 형태소 분석.
    ETRI 형태소 분석 결과를 완전히 대체하지는 않지만,
    한국어 텍스트의 형태소 분할 패턴을 보여주는 데 충분합니다.
    """
    morphs = []
    i = 0
    while i < len(text):
        c = text[i]

        # 한글 음절
        if '가' <= c <= '힣':
            # 종성 확인
            code = ord(c) - 0xAC00
            final = code % 28

            # 조사/어미 패턴 감지 (종성이 있는 음절 뒤에 오는 음절)
            if final != 0 and i + 1 < len(text):
                next_c = text[i + 1]
                if '가' <= next_c <= '힣':
                    next_code = ord(next_c) - 0xAC00
                    next_final = next_code % 28
                    # 다음 음절이 종성이 없으면 연결어미일 가능성
                    if next_final == 0:
                        # 현재 음절은 어간, 다음 음절은 연결어미
                        morphs.append({'text': c, 'type': 'VV', 'position': i})
                        morphs.append({'text': next_c, 'type': 'EC', 'position': i + 1})
                        i += 2
                        continue

            # 일반 명사/형용사 (단순 분류)
            # 초성 확인 — 특정 초성은 동사/형용사 가능성 높음
            initial = code // (21 * 28)
            if initial in (12, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25):
                # ㄱ,ㄲ,ㄴ,ㄷ,ㄸ,ㄹ,ㅁ,ㅂ,ㅃ,ㅅ,ㅆ,ㅇ,ㅈ,ㅉ,ㅊ,ㅋ,ㅌ,ㅍ,ㅎ — 동사/형용사 가능성
                # 단순화하여 VV(인용)으로 분류
                morphs.append({'text': c, 'type': 'VV', 'position': i})
            elif final != 0:
                # 종성이 있는 음절 — 명사일 가능성
                morphs.append({'text': c, 'type': 'NNG', 'position': i})
            else:
                # 종성이 없는 음절 (개음절)
                if i + 1 < len(text):
                    next_c = text[i + 1]
                    if '가' <= next_c <= '힣':
                        next_code = ord(next_c) - 0xAC00
                        next_final = next_code % 28
                        if next_final == 0:
                            # 다음 음절이 종성이 없음 — 현재가 조사/어미일 가능성
                            morphs.append({'text': c, 'type': 'EC', 'position': i})
                        else:
                            morphs.append({'text': c, 'type': 'NNG', 'position': i})
                    else:
                        morphs.append({'text': c, 'type': 'NNG', 'position': i})
                else:
                    morphs.append({'text': c, 'type': 'NNG', 'position': i})
            i += 1

        # 한글 자모
        elif 'ᄀ' <= c <= 'ᇿ' or '㄰' <= c <= '㆏':
            morphs.append({'text': c, 'type': 'SN', 'position': i})
            i += 1

        # 영문
        elif c.isascii() and c.isalpha():
            start = i
            while i + 1 < len(text) and text[i + 1].isascii() and text[i + 1].isalpha():
                i += 1
            token = text[start:i + 1]
            morphs.append({'text': token, 'type': 'SL', 'position': start})
            i += 1

        # 숫자
        elif c.isdigit():
            start = i
            while i + 1 < len(text) and text[i + 1].isdigit():
                i += 1
            token = text[start:i + 1]
            morphs.append({'text': token, 'type': 'SL', 'position': start})
            i += 1

        # 띄어쓰기
        elif c.isspace():
            morphs.append({'text': c, 'type': 'Space', 'position': i})
            i += 1

        # 구두점
        elif c in '.,!?;:()[]{}"\'-–—/\\@#$%^&*+=<>|_~`':
            morphs.append({'text': c, 'type': 'SF', 'position': i})
            i += 1

        # 기타 문자 (이모지, 기호 등)
        else:
            morphs.append({'text': c, 'type': 'SF', 'position': i})
            i += 1

    return morphs


# ═══════════════════════════════════════════════════════════════════
# 5. 유틸리티 함수
# ═══════════════════════════════════════════════════════════════════

def get_vocab_size(tokenizer) -> int:
    if hasattr(tokenizer, "vocab") and tokenizer.vocab:
        return len(tokenizer.vocab)
    if hasattr(tokenizer, "get_vocab"):
        return len(tokenizer.get_vocab())
    return -1


def get_vocab_size_tiktoken(encoder) -> int:
    try:
        if hasattr(encoder, "n_vocab"):
            return encoder.n_vocab
        return -1
    except Exception:
        return -1


# ═══════════════════════════════════════════════════════════════════
# 4b. ETRI-style morphological analysis
# ═══════════════════════════════════════════════════════════════════
def get_elt_tags(morphs: list[dict]) -> list[tuple[str, str]]:
    """
    ETRI 형태소 분석 결과에서 (형태소 텍스트, ETRI POS 태그) 쌍을 반환.

    Rules:
    - 동사/형용사의 연결어미(VC)는 문맥에 따라 EC 또는 CF로 분류:
      * 문장 중간(뒤에 명사구/비종결어미가 오는 경우) → EC
      * 문장 끝(비종결어미가 없는 경우) → CF
    - 일반 명사구, 부사구, 감탄사 등은 그대로 유지
    """
    result = []
    n = len(morphs)
    for i, m in enumerate(morphs):
        tag = m.get('type', '')
        text = m.get('text', '')

        if tag.startswith('VV') or tag.startswith('VA'):
            # 동사/형용사 — 원문 그대로
            result.append((text, tag))
        elif tag == 'EC':
            # 특수 처리: 연결어미를 문장 내 위치 파악
            # 뒤에 오는 형태소가 VV/VA/m(의미형태소)이면 EC 유지
            # 뒤에 오는 형태소가 없거나 종결어미면 CF
            if i + 1 < n:
                next_tag = morphs[i + 1].get('type', '')
                if next_tag.startswith('VV') or next_tag.startswith('VA') or next_tag == 'm':
                    result.append((text, 'EC'))
                else:
                    result.append((text, 'CF'))
            else:
                result.append((text, 'CF'))
        elif tag == 'EF':
            # 문장 종결어미는 위치가 문장이면 EF, 연결되면 EC
            if i + 1 < n:
                next_tag = morphs[i + 1].get('type', '')
                if next_tag in ('EF', 'EC', 'CF'):
                    result.append((text, 'EC'))
                else:
                    result.append((text, 'EF'))
            else:
                result.append((text, 'EF'))
        else:
            result.append((text, tag))
    return result


def get_lang_type(text: str) -> str:
    """
    텍스트의 언어 유형을 판단합니다.
    - 'korean': 한글(Hangul)이 포함되어 있음
    - 'english': 영문(Latin)이 포함되어 있음
    - 'mixed': 한글과 영문이 모두 포함되어 있음
    - 'other': 한글과 영문 모두 포함되지 않음
    """
    has_korean = any('가' <= c <= '힣' for c in text)
    has_english = any(c.isascii() and c.isalpha() for c in text)

    if has_korean and has_english:
        return 'mixed'
    elif has_korean:
        return 'korean'
    elif has_english:
        return 'english'
    else:
        return 'other'


def html_highlight_tokens(
    tokens: list[tuple[str, int, int]], text: str, color: str
) -> str:
    """
    토큰 (문자열, start, end) 리스트를 HTML로 하이라이트하여 표시
    원문 텍스트를 span으로 감싸서 토큰 경계를 시각적으로 표시
    """
    if not tokens:
        return escape_html(text)

    sorted_tokens = sorted(tokens, key=lambda x: x[1])

    filtered = []
    last_end = 0
    for token_str, start, end in sorted_tokens:
        if start < last_end:
            continue
        if start >= len(text):
            continue
        actual_end = min(end, len(text))
        if start < actual_end and token_str:
            filtered.append((token_str, start, actual_end))
            last_end = actual_end

    html_parts = []
    cursor = 0
    for token_str, start, end in filtered:
        if start > cursor:
            html_parts.append(escape_html(text[cursor:start]))
        display_token = escape_html(token_str)
        if not display_token:
            display_token = "␣"  # 빈 토큰 대체 (SPECIAL)

        html_parts.append(
            f'<span style="'
            f'background-color: {color}; '
            f'opacity: 0.40; '
            f'padding: 3px 8px; '
            f'border-radius: 5px; '
            f'margin: 2px; '
            f'display: inline-block; '
            f'font-weight: 600; '
            f'border: 1.5px solid {color}; '
            f'">{display_token}</span>'
        )
        cursor = end

    if cursor < len(text):
        html_parts.append(escape_html(text[cursor:]))

    return "".join(html_parts)


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("\n", "<br>")
    )


# ── Per-token color palette (distinguishable colors) ──
# Each token gets a distinct color; cycled if we run out.
TOKEN_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
    "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
    "#F8C471", "#82E0AA", "#F1948A", "#AED6F1", "#D7BDE2",
    "#A3E4D7", "#FAD7A0", "#ABEBC6", "#D5D8DC", "#AED6F1",
    "#A9DFBF", "#F9E79F", "#D5F5E3", "#FCF3CF", "#D4E6F1",
    "#D9EAD3", "#FADBD8", "#D5F5E3", "#A9DFBF", "#FAD7A0",
    "#AED6F1", "#D7BDE2", "#85C1E9", "#F8C471", "#98D8C8",
    "#DDA0DD", "#45B7D1", "#4ECDC4", "#96CEB4", "#FFEAA7",
    "#FF6B6B", "#F1948A", "#A3E4D7", "#BB8FCE", "#F7DC6F",
    "#82E0AA", "#FAD7A0", "#96CEB4", "#D5D8DC", "#A9DFBF",
]


def get_token_colors(n: int) -> list[str]:
    """
    Get distinguishable colors for n tokens.
    Each token gets a different color from the palette, cycling if needed.
    Adjacent tokens are guaranteed to have different colors.
    """
    colors = []
    palette_len = len(TOKEN_COLORS)
    offset = 0
    for i in range(n):
        color = TOKEN_COLORS[(i + offset) % palette_len]
        # Ensure adjacent tokens have different colors
        if colors and colors[-1] == color:
            # Shift by 1 to get a different color
            color = TOKEN_COLORS[(i + offset + 1) % palette_len]
            offset += 1  # Advance offset so next iteration skips the duplicate
        colors.append(color)
    return colors


# ═══════════════════════════════════════════════════════════════════
# 6. 토큰 시각화 렌더링
# ═══════════════════════════════════════════════════════════════════

def render_token_visualization(
    tokenize_result: list[tuple[str, int, int]] | dict,
    model_info: dict,
    text: str,
):
    """모델의 토큰 분할 결과를 시각적으로 표시 — 토큰마다 서로 다른 색상 사용"""
    display_name = model_info["display_name"]

    # tokenize_result는 list[tuple] 또는 dict일 수 있음
    if isinstance(tokenize_result, dict):
        tokens = tokenize_result.get('tokens', [])
        elt_output = tokenize_result.get('elt_output')
        elt_morphs = tokenize_result.get('elt_morphs')
        lang_type = tokenize_result.get('lang_type', 'unknown')
        byte_count = tokenize_result.get('byte_count', 0)
    else:
        tokens = tokenize_result
        elt_output = None
        elt_morphs = None
        lang_type = 'unknown'
        byte_count = 0

    num_tokens = len(tokens)
    vocab_size = model_info.get("vocab_size", "N/A")

    st.markdown(f"### 🔍 **{display_name}**의 토큰 분할 결과")
    st.caption(
        f"📊 총 **{num_tokens}개**의 토큰으로 분할  |  "
        f"vocab: {vocab_size:,}  |  {model_info['category']}"
    )

    # 원문 참조
    st.markdown(f"**원문**: `{text}`  ")
    st.caption(f"문장 길이: {len(text)}자  |  토큰/문자 비율: {num_tokens / max(len(text), 1):.2f}")

    # 각 토큰에 서로 다른 색상 할당
    token_colors = get_token_colors(num_tokens)

    # HTML 생성: 각 토큰 span에 개별 색상 적용
    sorted_tokens = sorted(tokens, key=lambda x: x[1])

    filtered = []
    last_end = 0
    for token_str, start, end in sorted_tokens:
        if start < last_end:
            continue
        if start >= len(text):
            continue
        actual_end = min(end, len(text))
        if start < actual_end and token_str:
            filtered.append((token_str, start, actual_end))
            last_end = actual_end

    # Get per-token colors for filtered tokens
    filtered_colors = get_token_colors(len(filtered))

    html_parts = []
    cursor = 0
    for idx, (token_str, start, end) in enumerate(filtered):
        if start > cursor:
            html_parts.append(escape_html(text[cursor:start]))

        display_token = escape_html(token_str)
        if not display_token:
            display_token = "␣"

        token_color = filtered_colors[idx]
        html_parts.append(
            f'<span style="'
            f'background-color: {token_color}; '
            f'opacity: 0.40; '
            f'padding: 3px 8px; '
            f'border-radius: 5px; '
            f'margin: 2px; '
            f'display: inline-block; '
            f'font-weight: 600; '
            f'border: 1.5px solid {token_color}; '
            f'">{display_token}</span>'
        )
        cursor = end

    if cursor < len(text):
        html_parts.append(escape_html(text[cursor:]))

    html = "".join(html_parts)

    # 색상 팔레트 범례
    legend_parts = []
    for i, tc in enumerate(filtered_colors):
        display_t = filtered[i][0].replace("▁", "␣").replace(" ", "␣(공백)")

        if display_t == "␣":
            display_t = "␣(공백)"
        elif not display_t:
            display_t = "␣(공백)"

        legend_parts.append(f'<span style="background-color: {tc}; padding: 2px 6px; border-radius: 3px; margin: 2px;">{display_t}</span>')

    st.markdown(
        f'<div style="'
        f'background-color: #f8f9fa; '
        f'border: 2.5px solid #dee2e6; '
        f'border-radius: 12px; '
        f'padding: 24px 20px; '
        f'font-size: 20px; '
        f'line-height: 2.6; '
        f'word-break: keep-all; '
        f'white-space: pre-wrap; '
        f'font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", "Segoe UI", sans-serif;'
        f'">'
        f'{html}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ETRI 형태소 분석 결과 표시 (한글 텍스트인 경우)
    if elt_output and elt_morphs:
        st.markdown("#### 📝 ETRI 형태소 분석 결과 (한국어)")
        st.caption(
            f"📊 언어 유형: **{lang_type}**  |  "
            f"비-한글 문자 바이트 수: **{byte_count}**  |  "
            f"형태소 수: **{len(elt_morphs)}**"
        )
        # ETRI 분석 결과를 읽기 쉬운 형태로 표시
        st.code(elt_output, language="text", line_numbers=False)

    # 토큰 상세 목록 (색상 표시 포함)
    st.markdown("#### 📋 토큰 상세 목록")
    cols_per_row = 8
    token_display_parts = []
    for i, (token_str, start, end) in enumerate(tokens):
        display = token_str.replace("▁", "␣")  # ▁ → ␣
        if display == "␣":
            display = "␣(공백)"
        elif display == " ":
            display = "␣(공백)"
        token_color = token_colors[i] if i < len(token_colors) else TOKEN_COLORS[i % len(TOKEN_COLORS)]
        # Use markdown colored span if possible, else just backtick
        token_display_parts.append(
            f'<span style="background-color: {token_color}; padding: 2px 6px; border-radius: 3px; margin: 2px;">`{display}`</span>'
        )

    for row_start in range(0, len(token_display_parts), cols_per_row):
        row_tokens = token_display_parts[row_start : row_start + cols_per_row]
        st.markdown(" ".join(row_tokens), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 7. 메인 UI
# ═══════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="LLM 토크나이저 비교 데모",
        page_icon="\U0001f524",
        layout="wide",
    )

    # ── 상단 타이틀 ──
    st.title("\U0001f524 LLM 토크나이저 비교 데모")
    st.caption(
        "같은 텍스트가 모델마다 어떻게 다르게 토큰으로 나뉘는지 비교해보세요. "
        "특히 **한글**과 **영어**의 토큰 분할 차이를 확인해보세요!"
    )
    st.divider()

    # ── 사이드바: 모델 선택 ──
    st.sidebar.header("\U0001f4e6 모델 선택")
    st.sidebar.markdown("---")

    open_weight_selected = st.sidebar.toggle(
        "오픈웨이트 모델 (HuggingFace)",
        value=True,
        help="K-EXAONE, EXAONE, Qwen, GLM, Kimi, Gemma 등 공개 모델",
    )
    gpt_selected = st.sidebar.toggle(
        "GPT 계열 (OpenAI)",
        value=True,
        help="GPT-4o, GPT-4, GPT-3.5, GPT-2 등 tiktoken 기반 모델",
    )
    gated_selected = st.sidebar.toggle(
        "Gated 모델 (HF 승인 필요)",
        value=True,
        help="Llama-3.1 8B Instruct 등 HF 승인이 필요한 gated 모델",
    )
    active_models = {}
    if open_weight_selected:
        active_models.update({k: v for k, v in OPEN_WHEIGHT_MODELS.items()})
    if gpt_selected:
        active_models.update({k: v for k, v in GPT_FAMILY_MODELS.items()})
    if gated_selected:
        active_models.update({k: v for k, v in GATED_MODELS.items()})

    available_models = {}
    unavailable_models = []
    for key, info in active_models.items():
        if info["type"] == "hf" or info["type"] == "hf_gated":
            if load_hf_tokenizer(key, info) is not None:
                available_models[key] = info
            else:
                unavailable_models.append(key)
        elif info["type"] == "tiktoken":
            if get_tiktoken_encoder(key) is not None:
                available_models[key] = info
            else:
                unavailable_models.append(key)

    if unavailable_models:
        st.sidebar.warning(f"⚠️ {len(unavailable_models)}개 모델은 현재 사용 불가:")
        for key in unavailable_models:
            info = active_models.get(key, {})
            st.sidebar.warning(
                f"  • {info.get('display_name', key)} — {info.get('status', '사용 불가')}"
            )

    if not available_models:
        st.error(
            "❌ 사용 가능한 모델이 없습니다. 토글을 확인하거나 토크나이저를 다운로드해주세요."
        )
        st.stop()

    # 토크나이저 미리 로드 (캐싱됨)
    tokenizers = {}
    for key in list(available_models.keys()):
        tokenizers[key] = load_model_tokenizer(key)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**ℹ️ 참고사항**")
    st.sidebar.info(
        "• **오픈웨이트 모델**: 모두 로컬에 토크나이저가 저장되어 있어 오프라인 사용 가능\n"
        "• **GPT 계열**: tiktoken 라이브러리로 토큰화 (계정 불필요)\n"
        "• **vocab size** ≠ **토큰 수**: vocab이 크다고 토큰이 적게 나뉘는 것은 아님\n"
        "• **한글 처리**: 모델마다 자소/바이트/형태소 등 방식이 다름 → 차이가 명확함\n"
        "• **Solar Open2**: 로컬 토크나이저 호환성 문제로 제외됨"
    )

    # ── 메인 영역: 입력 ──
    st.subheader("\U0001f4dd 입력 텍스트")

    # 세션 상태 초기화
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""

    # 예시 텍스트 버튼 (클릭 시 입력창 채우기)
    st.markdown(
        "**예시 텍스트** — 클릭하여 입력창에 채우기 (필수는 아니며, 직접 입력도 가능)"
    )
    sample_cols = st.columns(len(SAMPLE_TEXTS))
    sample_keys = list(SAMPLE_TEXTS.keys())
    for i, key in enumerate(sample_keys):
        with sample_cols[i]:
            label = key.replace("_", " ")
            if st.button(
                label=label,
                key=f"sample_btn_{key}",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state.input_text = SAMPLE_TEXTS[key]
                st.session_state.analysis_run = False  # 이전 분석 결과 초기화
                st.rerun()

    # 텍스트 입력창 (초기에는 비어있음)
    input_text = st.text_area(
        "텍스트 입력",
        value=st.session_state.input_text,
        height=120,
        key="input_text",
        label_visibility="collapsed",
        placeholder="여기에 분석할 텍스트를 직접 입력하세요...",
        help="직접 입력하거나 위의 예시 텍스트 버튼을 클릭하세요",
    )

    # 토큰화 실행 버튼
    if st.button("\U0001f50d 토큰화 실행", type="primary", use_container_width=True):
        if not input_text or not input_text.strip():
            st.warning("⚠️ 분석할 텍스트를 입력해주세요.")
        else:
            st.session_state.analysis_run = True
            results = {}
            for key in list(available_models.keys()):
                tokenizer_or_encoder = tokenizers.get(key)
                if tokenizer_or_encoder is None:
                    continue
                try:
                    if key in GPT_FAMILY_MODELS:
                        token_result = tokenize_tiktoken_with_analysis(tokenizer_or_encoder, input_text)
                        results[key] = {
                            "tokens": token_result["tokens"],
                            "num_tokens": len(token_result["tokens"]),
                            "vocab_size": get_vocab_size_tiktoken(tokenizer_or_encoder),
                            "elt_output": token_result["elt_output"],
                            "elt_morphs": token_result["elt_morphs"],
                            "lang_type": token_result["lang_type"],
                            "byte_count": token_result["byte_count"],
                        }
                    else:
                        token_result = tokenize_hf_with_analysis(tokenizer_or_encoder, input_text, key)
                        results[key] = {
                            "tokens": token_result["tokens"],
                            "num_tokens": len(token_result["tokens"]),
                            "vocab_size": get_vocab_size(tokenizer_or_encoder),
                            "elt_output": token_result["elt_output"],
                            "elt_morphs": token_result["elt_morphs"],
                            "lang_type": token_result["lang_type"],
                            "byte_count": token_result["byte_count"],
                        }
                except Exception as e:
                    st.error(
                        f"{active_models[key]['display_name']} 처리 중 오류: {e}"
                    )

            st.session_state.analysis_results = results
            st.session_state.analysis_input = input_text

    # 분석 후 입력이 변경되면 결과 초기화
    if (
        st.session_state.get("analysis_run")
        and st.session_state.get("analysis_input") != input_text
    ):
        st.session_state.analysis_run = False

    # ── 메인 영역: 결과 ──
    if st.session_state.get("analysis_run") and st.session_state.get(
        "analysis_results"
    ):
        results = st.session_state.analysis_results
        input_text = st.session_state.analysis_input

        # ── 1. 토큰 수 비교 테이블 ──
        st.subheader("\U0001f4ca 토큰 수 비교")

        comparison_data = {
            "모델": [],
            "벤더": [],
            "토큰 수": [],
            "vocab size": [],
            "토큰/문자 비율": [],
            "avg 토큰 길이": [],
            "카테고리": [],
        }

        for key in list(available_models.keys()):
            if key not in results:
                continue
            r = results[key]
            info = active_models[key]
            token_lengths = [len(t[0]) for t in r["tokens"]]
            avg_len = sum(token_lengths) / max(len(token_lengths), 1)
            ratio = r["num_tokens"] / max(len(input_text), 1)

            comparison_data["모델"].append(info["display_name"])
            comparison_data["벤더"].append(info["vendor"])
            comparison_data["토큰 수"].append(r["num_tokens"])
            comparison_data["vocab size"].append(r["vocab_size"])
            comparison_data["토큰/문자 비율"].append(f"{ratio:.2f}")
            comparison_data["avg 토큰 길이"].append(f"{avg_len:.1f}")
            comparison_data["카테고리"].append(info["category"])

        st.dataframe(
            comparison_data,
            use_container_width=True,
            hide_index=True,
        )

        # 막대 차트
        chart_data = {"모델": [], "토큰 수": []}
        for key in list(available_models.keys()):
            if key not in results:
                continue
            info = active_models[key]
            chart_data["모델"].append(info["display_name"])
            chart_data["토큰 수"].append(results[key]["num_tokens"])

        st.bar_chart(
            data=chart_data,
            x="모델",
            y="토큰 수",
            color="#4ECDC4",
            use_container_width=True,
        )

        # ── 2. 토큰 시각화 (모든 모델 한 번에 표시) ──
        st.divider()
        st.subheader("\U0001f50d 토큰 시각화")

        st.markdown(
            "각 모델이 같은 텍스트를 어떻게 다른 토큰으로 나누는지 **모델별로 한 번에** 확인할 수 있습니다. "
            "같은 모델의 토큰들은 서로 **다른 색상**으로 표시되어 토큰 경계를 쉽게 구분할 수 있습니다."
        )

        results_keys = list(results.keys())
        for key in results_keys:
            info = active_models[key]
            info_with_vocab = {**info, "vocab_size": results[key]["vocab_size"]}
            render_token_visualization(
                results[key], info_with_vocab, input_text
            )
            # 각 모델 간 구분선
            if key != results_keys[-1]:
                st.divider()

    # ── 하단 정보 ──
    st.divider()
    st.markdown(
        """
    **데모 소개**
    - 이 데모는 K-EXAONE, EXAONE 4.5, Qwen3.6, GLM-5.2, Kimi K2.5, Gemma 4 및 GPT 계열(GPT-4o, GPT-4, GPT-3.5, GPT-2) 등 다양한 LLM 모델의 토크나이저를 비교합니다.
    - 같은 텍스트라도 모델마다 토큰 수가 다릅니다 — 이는 토크나이제이션 알고리즘과 언어별 처리 방식의 차이 때문입니다.
    - 특히 **한글**은 자소/형태소/바이트 단위로 분할되는 방식이 모델마다 크게 달라 비교가 더욱 흥미롭습니다.
    - **GPT 계열**은 tiktoken(Backward-compatible BPE)를 사용하며, **오픈웨이트 모델**은 HuggingFace Transformers를 사용합니다.

    **사용된 토크나이저**
    - HuggingFace Transformers `AutoTokenizer`를 사용하여 오픈웨이트 모델의 토크나이저 로드
    - OpenAI `tiktoken`을 사용하여 GPT 계열 모델의 토크나이저 로드
    - 모든 토크나이저는 `tokenizer.json` 또는 tiktoken 인코딩 테이블로 로컬에 저장
    """
    )


if __name__ == "__main__":
    main()
