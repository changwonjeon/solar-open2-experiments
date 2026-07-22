"""
LLM 토크나이저 비교 데모
 - HuggingFace open-weight 모델 7개 + DeepSeek-V3 + GPT계열(tiktoken) 토크나이저 비교
 - 한글/영어 텍스트 입력 시 토큰 수 및 토큰 분할 방식 시각화
 - 오프라인 지원: 모든 토크나이저 로컬에 저장됨 (HuggingFace/OpenAI 계정 불필요 — 단, Llama-4, Gemma-4는 HF 로그인 필요)
"""
import json
import os
import sys
from typing import Optional

import streamlit as st
import tiktoken
from transformers import AutoTokenizer

# ─────────────────────────────────────────────
# 1. 모델 메타데이터
# ─────────────────────────────────────────────
# Base: 공개 오픈웨이트 모델 (HuggingFace에서 다운로드, 대부분 계정 없이 가능)
OPEN_WHEIGHT_MODELS = {
    "upstage-solar-pro2-tokenizer": {
        "display_name": "Solar Open2 (Tokenizer)",
        "full_name": "Solar Open2 토크나이저",
        "vendor": "Upstage",
        "repo": "https://huggingface.co/upstage/solar-pro2-tokenizer",
        "official_model": "upstage/Solar-Open2-250B",
        "category": "Korean↔Open",
        "color": "#FF6B6B",      # Upstage red
        "status": "✅ 로컬 저장 완료",
        "type": "hf",
    },
    "LGAI-EXAONE-K-EXAONE-236B-A23B": {
        "display_name": "K-EXAONE 236B",
        "full_name": "K-EXAONE 236B-A23B",
        "vendor": "LG AI Research",
        "repo": "https://huggingface.co/LGAI-EXAONE/K-EXAONE-236B-A23B",
        "official_model": "LGAI-EXAONE/K-EXAONE-236B-A23B",
        "category": "Korean↔Open",
        "color": "#4ECDC4",      # LG teal
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
        "color": "#45B7D1",      # Blue
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
        "color": "#7B68EE",      # Purple
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
        "color": "#2ECC71",      # Green
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
        "color": "#9B59B6",      # Dark purple
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
        "color": "#F39C12",      # Orange
        "status": "✅ 로컬 저장 완료",
        "type": "hf",
    },
    "deepseek-ai-DeepSeek-V3": {
        "display_name": "DeepSeek-V3",
        "full_name": "DeepSeek-V3 (MoE 671B)",
        "vendor": "DeepSeek",
        "repo": "https://huggingface.co/deepseek-ai/DeepSeek-V3",
        "official_model": "deepseek-ai/DeepSeek-V3",
        "category": "Global↔Open",
        "color": "#1ABC9C",      # Turquoise
        "status": "✅ 로컬 저장 완료",
        "type": "hf",
    },
    "deepseek-ai-DeepSeek-R1": {
        "display_name": "DeepSeek-R1",
        "full_name": "DeepSeek-R1 (추론 특화 685B)",
        "vendor": "DeepSeek",
        "repo": "https://huggingface.co/deepseek-ai/DeepSeek-R1",
        "official_model": "deepseek-ai/DeepSeek-R1",
        "category": "Global↔Open",
        "color": "#16A085",      # Darker turquoise
        "status": "🔒 HF 로그인 필요",
        "type": "hf_gated",
        "hf_model_id": "deepseek-ai/DeepSeek-R1",
    },
}

# GPT-family models via tiktoken (OpenAI)
GPT_FAMILY_MODELS = {
    "gpt-4o": {
        "display_name": "GPT-4o",
        "full_name": "GPT-4 Omni",
        "vendor": "OpenAI",
        "repo": "https://openai.com/index/gpt-4/",
        "official_model": "gpt-4o",
        "category": "Global↔Proprietary",
        "color": "#00A2FF",      # OpenAI blue
        "status": "✅ tiktoken 내장",
        "type": "tiktoken",
        "tiktoken_name": "o200k_base",
    },
    "gpt-4-turbo": {
        "display_name": "GPT-4 Turbo",
        "full_name": "GPT-4 Turbo (128K)",
        "vendor": "OpenAI",
        "repo": "https://openai.com/index/gpt-4/",
        "official_model": "gpt-4-turbo",
        "category": "Global↔Proprietary",
        "color": "#0081CB",      # Darker OpenAI blue
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
        "color": "#0066CC",      # Classic OpenAI blue
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
        "color": "#004BB5",      # GPT-3.5 blue
        "status": "✅ tiktoken 내장",
        "type": "tiktoken",
        "tiktoken_name": "cl100k_base",
    },
    "gpt-2": {
        "display_name": "GPT-2",
        "full_name": "GPT-2 (124M/355M/774M/1.5B)",
        "vendor": "OpenAI",
        "repo": "https://openai.com/blog/gpt-2-150m/",
        "official_model": "gpt-2",
        "category": "Global↔Proprietary",
        "color": "#003399",      # GPT-2 dark blue
        "status": "✅ tiktoken 내장",
        "type": "tiktoken",
        "tiktoken_name": "gpt2",
    },
}

# Gated models — need HuggingFace account + HF_TOKEN
GATED_MODELS = {
    "meta-llama-Llama-4-Maverick": {
        "display_name": "Llama-4 Maverick 17B",
        "full_name": "Llama-4 Maverick 17B-128E (402B MoE)",
        "vendor": "Meta",
        "repo": "https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct",
        "official_model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
        "category": "Global↔Gated",
        "color": "#E74C3C",      # Red
        "status": "🔒 HF 로그인 필요",
        "type": "hf_gated",
        "hf_model_id": "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
    },
}

# Combine all models
ALL_MODELS = {**OPEN_WHEIGHT_MODELS, **GPT_FAMILY_MODELS, **GATED_MODELS}

BASE_MODEL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models"
)


# ─────────────────────────────────────────────
# 2. 토크나이저 캐싱
# ─────────────────────────────────────────────
@st.cache_resource
def load_hf_tokenizer(model_key: str) -> Optional[AutoTokenizer]:
    """HuggingFace 토크나이저를 로드 (캐싱됨)"""
    if model_key in GPT_FAMILY_MODELS or model_key in GATED_MODELS:
        return None

    model_dir = os.path.join(BASE_MODEL_DIR, model_key)
    if not os.path.isdir(model_dir):
        return None

    try:
        # 먼저 fast tokenizer 시도 (offset_mapping 지원)
        tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            use_fast=True,
            local_files_only=True,
        )
        return tokenizer
    except Exception:
        # fast 실패 시 slow tokenizer 재시도
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_dir,
                use_fast=False,
                local_files_only=True,
            )
            return tokenizer
        except Exception:
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
        encoder = tiktoken.get_encoding(tiktoken_name)
        return encoder
    except Exception:
        return None


def load_model_tokenizer(model_key: str):
    """
    모델 키에 따라 적절한 토크나이저를 로드
    - HF 모델: AutoTokenizer 로드
    - GPT 계열: tiktoken 인코더 로드
    - Gated 모델: HF_TOKEN이 있으면 로드, 아니면 None
    """
    if model_key in GPT_FAMILY_MODELS:
        return get_tiktoken_encoder(model_key)
    elif model_key in GATED_MODELS:
        # HF_TOKEN 환경변수 확인
        hf_token = os.environ.get("HF_TOKEN", "")
        if hf_token:
            try:
                from transformers import AutoTokenizer
                hf_model_id = GATED_MODELS[model_key].get("hf_model_id")
                tokenizer = AutoTokenizer.from_pretrained(
                    hf_model_id,
                    use_fast=True,
                )
                return tokenizer
            except Exception:
                return None
        return None
    else:
        return load_hf_tokenizer(model_key)


# ─────────────────────────────────────────────
# 3. 샘플 텍스트
# ─────────────────────────────────────────────
SAMPLE_TEXTS = {
    "짧은_한글": (
        "인공지능은 우리의 삶을 바꾸고 있다."
    ),
    "짧은_영문": (
        "AI changes everything."
    ),
    "한영_혼합_짧은": (
        "GenAI like GPT, Claude, Gemini — 한국어 처리는 Solar와 EXAONE이 강점이다."
    ),
    "기술_짧은": (
        "토크나이제이션은 BPE, WordPiece, SentencePiece 알고리즘을 사용한다."
    ),
}


# ─────────────────────────────────────────────
# 4. 토크나이즈 함수
# ─────────────────────────────────────────────
def tokenize_hf(tokenizer, text: str) -> list[tuple[str, int, int]]:
    """
    HuggingFace 토크나이저로 텍스트 토큰화
    Returns: list of (token_string, start_offset, end_offset)
    """
    try:
        # Fast tokenizer 시도 (offset_mapping 지원)
        encoding = tokenizer(text, return_offsets_mapping=True)
        result = []
        for token_id, (start, end) in zip(encoding.input_ids, encoding.offset_mapping):
            if start == 0 and end == 0:
                continue  # special tokens (CLS, SEP, PAD 등)
            token_str = text[start:end]
            result.append((token_str, start, end))
        return result
    except Exception:
        # Slow tokenizer fallback
        try:
            encoding = tokenizer(text, add_special_tokens=False)
            tokens = tokenizer.convert_ids_to_tokens(encoding.input_ids)
            if not tokens:
                # LlamaTokenizer 한글 한계: vocab에 한글 음절이 없음
                # 인코딩이 안 되었으므로 바이트 단위로 fallback
                return _tokenize_bytes_fallback(text)

            result = []
            pos = 0
            for token in tokens:
                # BPE 토큰의 ▁ 접두사 처리 (▁ = 공백)
                if token.startswith("▁"):
                    token_str = " " + token[1:]
                elif isinstance(token, bytes):
                    try:
                        token_str = token.decode("utf-8")
                    except UnicodeDecodeError:
                        token_str = token.decode("utf-8", errors="replace")
                else:
                    token_str = str(token)

                # 토큰 문자열에서 ▁를 공백으로 변환 (양쪽 모두)
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
    """
    바이트 단위 fallback 토큰화
    UTF-8 인코딩된 바이트를 개별적으로 토큰으로 표시
    """
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
        # tiktoken은 바이트 수준 BPE로 인코딩
        # 디코딩으로 토큰 문자열 얻기
        tokens = []
        pos = 0
        for token_id in token_ids:
            try:
                # 토큰 바이트 디코딩
                token_bytes = encoder.decode_single_token_bytes(token_id)
                token_str = token_bytes.decode("utf-8", errors="replace")
            except Exception:
                token_str = f"[{token_id}]"

            # 텍스트에서 토큰의 위치 찾기 (근사치)
            idx = text.find(token_str, pos)
            if idx != -1:
                end = idx + len(token_str)
                tokens.append((token_str, idx, end))
                pos = end
            else:
                # 매칭 불가 — 근사 위치 사용
                tokens.append((token_str, pos, pos + len(token_str)))
                pos += len(token_str)
        return tokens
    except Exception:
        return _tokenize_bytes_fallback(text)


# ─────────────────────────────────────────────
# 5. 유틸리티 함수
# ─────────────────────────────────────────────
def get_vocab_size(tokenizer) -> int:
    """토크나이저의 vocab size 반환"""
    if hasattr(tokenizer, 'vocab') and tokenizer.vocab:
        return len(tokenizer.vocab)
    if hasattr(tokenizer, 'get_vocab'):
        return len(tokenizer.get_vocab())
    return -1


def get_vocab_size_tiktoken(encoder) -> int:
    """tiktoken 인코더의 vocab size 반환"""
    try:
        # tiktoken의 vocab 크기는 보통 50257 (GPT-2) 또는 100257 (cl100k), 200000 (o200k)
        # 정확한 크기를 얻는 방법
        if hasattr(encoder, 'n_vocab'):
            return encoder.n_vocab
        # fallback: 인코딩된 토큰 범위 추정
        return -1
    except Exception:
        return -1


def html_highlight_tokens(tokens: list[tuple[str, int, int]], text: str, color: str) -> str:
    """
    토큰 (문자열, start, end) 리스트를 HTML로 하이라이트하여 표시
    원문 텍스트를 span으로 감싸서 토큰 경계를 시각적으로 표시
    """
    if not tokens:
        return escape_html(text)

    # tokens를 start offset 기준으로 정렬
    sorted_tokens = sorted(tokens, key=lambda x: x[1])

    # 중복/겹침 제거 및 필터링
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

    # HTML 생성
    html_parts = []
    cursor = 0
    for token_str, start, end in filtered:
        # before this token
        if start > cursor:
            html_parts.append(escape_html(text[cursor:start]))

        # the token span
        display_token = escape_html(token_str)
        if not display_token:
            display_token = "␣"  # 빈 토큰 대체

        html_parts.append(
            f'<span style="'
            f'background-color: {color}; '
            f'opacity: 0.35; '
            f'padding: 2px 1px; '
            f'border-radius: 3px; '
            f'margin: 1px 0; '
            f'display: inline-block; '
            f'font-weight: 500; '
            f'">{display_token}</span>'
        )
        cursor = end

    # remaining
    if cursor < len(text):
        html_parts.append(escape_html(text[cursor:]))

    return "".join(html_parts)


def escape_html(text: str) -> str:
    """HTML 이스케이프"""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("\n", "<br>"))


# ─────────────────────────────────────────────
# 6. 메인 UI
# ─────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="LLM 토크나이저 비교 데모",
        page_icon="🔤",
        layout="wide",
    )

    # ── 상단 타이틀 ──
    st.title("🔤 LLM 토크나이저 비교 데모")
    st.caption(
        "같은 텍스트가 모델마다 어떻게 다르게 토큰으로 나뉘는지 비교해보세요. "
        "특히 **한글**과 **영어**의 토큰 분할 차이를 확인해보세요!"
    )

    # ── 사이드바 ──
    st.sidebar.header("📦 모델 선택")
    st.sidebar.markdown("---")

    # 카테고리별 토글
    open_weight_selected = st.sidebar.toggle(
        "오픈웨이트 모델 (HuggingFace)",
        value=True,
        help="Solar, EXAONE, Qwen, GLM, Kimi, Gemma, DeepSeek 등 공개 모델",
    )
    gpt_selected = st.sidebar.toggle(
        "GPT 계열 (OpenAI)",
        value=True,
        help="GPT-4, GPT-3.5, GPT-2 등 tiktoken 기반 GPT 모델",
    )
    gated_selected = st.sidebar.toggle(
        "Gated 모델 (HF 로그인 필요)",
        value=False,
        help="Llama-4 Maverick 등 HuggingFace 계정 필요 모델",
    )

    # 활성화된 모델 필터링
    active_models = {}
    if open_weight_selected:
        active_models.update({k: v for k, v in OPEN_WHEIGHT_MODELS.items()})
    if gpt_selected:
        active_models.update({k: v for k, v in GPT_FAMILY_MODELS.items()})
    if gated_selected:
        active_models.update({k: v for k, v in GATED_MODELS.items()})

    # 모델 가용성 체크
    available_models = {}
    unavailable_models = []
    for key, info in active_models.items():
        if info["type"] == "hf":
            if load_hf_tokenizer(key) is not None:
                available_models[key] = info
            else:
                unavailable_models.append(key)
        elif info["type"] == "tiktoken":
            if get_tiktoken_encoder(key) is not None:
                available_models[key] = info
            else:
                unavailable_models.append(key)
        elif info["type"] == "hf_gated":
            if os.environ.get("HF_TOKEN", ""):
                available_models[key] = info
            else:
                unavailable_models.append(key)

    if unavailable_models:
        st.sidebar.warning(f"⚠️ {len(unavailable_models)}개 모델은 현재 사용 불가:")
        for key in unavailable_models:
            info = active_models.get(key, {})
            st.sidebar.warning(f"  • {info.get('display_name', key)} — {info.get('status', '사용 불가')}")

    if not available_models:
        st.error("❌ 사용 가능한 모델이 없습니다. 토글을 확인하거나 토크나이저를 다운로드해주세요.")
        st.stop()

    # 모델 선택 멀티셀렉트
    all_model_names = [info["display_name"] for info in available_models.values()]
    selected_display_names = st.sidebar.multiselect(
        "비교할 모델 선택",
        options=all_model_names,
        default=all_model_names,
    )

    # 선택된 모델 키 매핑
    selected_keys = [
        key for key, info in available_models.items()
        if info["display_name"] in selected_display_names
    ]

    # 토크나이저 미리 로드 (캐싱됨)
    tokenizers = {}
    for key in selected_keys:
        tokenizers[key] = load_model_tokenizer(key)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**ℹ️ 참고사항**")
    st.sidebar.info(
        "• **오픈웨이트 모델**: 모두 로컬에 토크나이저가 저장되어 있어 오프라인 사용 가능\n"
        "• **GPT 계열**: tiktoken 라이브러리로 토큰화 (계정 불필요)\n"
        "• **Gated 모델**: HuggingFace 계정 필요 — `HF_TOKEN` 환경변수 설정 필요\n"
        "• **vocab size** ≠ **토큰 수**: vocab이 크다고 토큰이 적게 나뉘는 것은 아님\n"
        "• **한글 처리**: 모델마다 자소/바이트/형태소 등 방식이 다름 → 차이가 명확함\n"
        "• **Llama-4, Gemma-4**: HF 게이트웨이 통과 후 추가 다운로드 가능"
    )

    # ── 메인 영역 ──
    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("📝 입력 텍스트")

        text_type = st.radio(
            "텍스트 유형 선택",
            options=list(SAMPLE_TEXTS.keys()),
            format_func=lambda x: x.replace("_", " "),
            horizontal=True,
        )

        # 텍스트 에디터
        input_text = st.text_area(
            "텍스트 입력",
            value=SAMPLE_TEXTS[text_type],
            height=120,
            key="input_text",
            label_visibility="collapsed",
        )

        if st.button("🔍 토큰화 실행", type="primary", use_container_width=True):
            st.session_state.run_analysis = True

    with col2:
        st.subheader("📊 결과")

        if st.session_state.get("run_analysis", False) and input_text:
            # 각 모델별 토큰화 실행
            results = {}
            for key in selected_keys:
                tokenizer_or_encoder = tokenizers.get(key)
                if tokenizer_or_encoder is None:
                    continue
                try:
                    if key in GPT_FAMILY_MODELS:
                        tokens = tokenize_tiktoken(tokenizer_or_encoder, input_text)
                        vocab_size = get_vocab_size_tiktoken(tokenizer_or_encoder)
                    else:
                        tokens = tokenize_hf(tokenizer_or_encoder, input_text)
                        vocab_size = get_vocab_size(tokenizer_or_encoder)

                    results[key] = {
                        "tokens": tokens,
                        "num_tokens": len(tokens),
                        "vocab_size": vocab_size,
                    }
                except Exception as e:
                    st.error(f"{active_models[key]['display_name']} 처리 중 오류: {e}")

            if not results:
                st.error("🤔 결과를 생성할 수 없습니다. 다시 시도해주세요.")
                st.session_state.run_analysis = False
                return

            # ── 1. 토큰 수 비교 차트 ──
            st.markdown("### 📊 토큰 수 비교")

            chart_data = {
                "모델": [],
                "토큰 수": [],
                "vocab size": [],
            }
            for key in selected_keys:
                if key in results:
                    info = active_models[key]
                    chart_data["모델"].append(info["display_name"])
                    chart_data["토큰 수"].append(results[key]["num_tokens"])
                    chart_data["vocab size"].append(results[key]["vocab_size"])

            st.dataframe(
                chart_data,
                use_container_width=True,
                hide_index=True,
            )

            # 막대 차트
            st.bar_chart(
                data=chart_data,
                x="모델",
                y="토큰 수",
                color="#4ECDC4",
                use_container_width=True,
            )

            # ── 2. 상세 비교 테이블 ──
            st.markdown("### 📋 상세 비교")

            comparison_data = {
                "모델": [],
                "벤더": [],
                "토큰 수": [],
                "vocab size": [],
                "토큰/문자 비율": [],
                "avg 토큰 길이": [],
                "카테고리": [],
            }

            for key in selected_keys:
                if key not in results:
                    continue
                r = results[key]
                info = active_models[key]

                # avg 토큰 길이 계산
                token_lengths = [len(t[0]) for t in r["tokens"]]
                avg_len = sum(token_lengths) / max(len(token_lengths), 1)

                # 토큰/문자 비율
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

            # ── 3. 토큰 하이라이트 ──
            st.markdown("### 🔍 토큰 하이라이트")
            st.caption(
                "같은 텍스트가 모델마다 어떻게 다른 토큰으로 나뉘는지 시각적으로 확인하세요. "
                "각 색상 블록이 해당 모델의 토큰 경계를 나타냅니다."
            )

            # 모델별 2열 배치
            num_cols = 2
            num_rows = (len(selected_keys) + 1) // num_cols
            for row_idx in range(num_rows):
                cols = st.columns(num_cols)
                for col_idx in range(num_cols):
                    model_idx = row_idx * num_cols + col_idx
                    if model_idx >= len(selected_keys):
                        break
                    key = selected_keys[model_idx]
                    info = active_models[key]
                    r = results[key]

                    # 토큰 하이라이트 HTML 생성
                    html = html_highlight_tokens(r["tokens"], input_text, info["color"])

                    with cols[col_idx]:
                        st.markdown(f"**{info['display_name']}**")
                        st.caption(
                            f"{r['num_tokens']} 토큰 | "
                            f"vocab: {r['vocab_size']:,} | "
                            f"{info['category']}"
                        )
                        st.markdown(html, unsafe_allow_html=True)

            st.session_state.run_analysis = False
        else:
            st.info("👈 왼쪽에서 텍스트를 선택하고 **토큰화 실행** 버튼을 눌러주세요.")

    # ── 하단 정보 ──
    st.markdown("---")
    st.markdown("""
    **데모 소개**
    - 이 데모는 Solar Open2, K-EXAONE, EXAONE 4.5, Qwen3.6, GLM-5.2, Kimi K2.5, Gemma 4, DeepSeek-V3 및 GPT 계열(GPT-4o, GPT-4, GPT-3.5, GPT-2) 등 다양한 LLM 모델의 토크나이저를 비교합니다.
    - 같은 텍스트라도 모델마다 토큰 수가 다릅니다 — 이는 토크나이제이션 알고리즘과 언어별 처리 방식의 차이 때문입니다.
    - 특히 **한글**은 자소/형태소/바이트 단위로 분할되는 방식이 모델마다 크게 달라 비교가 더욱 흥미롭습니다.
    - **GPT 계열**은 tiktoken(Backward-compatible BPE)를 사용하며, **오픈웨이트 모델**은 HuggingFace Transformers를 사용합니다.

    **사용된 토크나이저**
    - HuggingFace Transformers `AutoTokenizer`를 사용하여 오픈웨이트 모델의 토크나이저 로드
    - OpenAI `tiktoken`을 사용하여 GPT 계열 모델의 토크나이저 로드
    - 모든 토크나이저는 `tokenizer.json` 또는 tiktoken 인코딩 테이블로 로컬에 저장
    """)


if __name__ == "__main__":
    main()
