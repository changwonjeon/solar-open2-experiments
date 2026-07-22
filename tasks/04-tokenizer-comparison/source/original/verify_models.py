#!/usr/bin/env python3
"""
토크나이저 모델 검증 스크립트
 - 로컬에 다운로드된 토크나이저가 정상 로드되는지 확인
 - 각 모델의 한글/영어 토큰화 결과 비교
 - 누락된 모델 확인
"""
import os
import sys
from transformers import AutoTokenizer
import tiktoken

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# 모델 정의 (데모에 포함된 모든 모델)
MODELS = {
    # HuggingFace 오픈웨이트 모델
    "upstage-solar-pro2-tokenizer": {
        "display_name": "Solar Open2 (Tokenizer)",
        "hf_repo": "upstage/solar-pro2-tokenizer",
        "type": "hf",
        "expected_vocab": 196608,
    },
    "LGAI-EXAONE-K-EXAONE-236B-A23B": {
        "display_name": "K-EXAONE 236B",
        "hf_repo": "LGAI-EXAONE/K-EXAONE-236B-A23B",
        "type": "hf",
        "expected_vocab": 153600,
    },
    "LGAI-EXAONE-EXAONE-4.5-33B": {
        "display_name": "EXAONE 4.5 33B",
        "hf_repo": "LGAI-EXAONE/EXAONE-4.5-33B",
        "type": "hf",
        "expected_vocab": 153600,
    },
    "Qwen-Qwen3.6-35B-A3B": {
        "display_name": "Qwen3.6 35B-A3B",
        "hf_repo": "Qwen/Qwen3.6-35B-A3B",
        "type": "hf",
        "expected_vocab": 248044,
    },
    "zai-org-GLM-5.2": {
        "display_name": "GLM-5.2",
        "hf_repo": "zai-org/GLM-5.2",
        "type": "hf",
        "expected_vocab": 154820,
    },
    "moonshotai-Kimi-K2.5": {
        "display_name": "Kimi K2.5",
        "hf_repo": "moonshotai/Kimi-K2.5",
        "type": "hf",
        "expected_vocab": 163584,
    },
    "google-gemma-4-31B-it": {
        "display_name": "Gemma 4 31B-IT",
        "hf_repo": "google/gemma-4-31B-it",
        "type": "hf",
        "expected_vocab": 262144,
    },
    "deepseek-ai-DeepSeek-V3": {
        "display_name": "DeepSeek-V3",
        "hf_repo": "deepseek-ai/DeepSeek-V3",
        "type": "hf",
        "expected_vocab": 128815,
    },
    "deepseek-ai-DeepSeek-V2.5": {
        "display_name": "DeepSeek-V2.5",
        "hf_repo": "deepseek-ai/DeepSeek-V2.5",
        "type": "hf",
        "expected_vocab": 100018,
    },
    "deepseek-ai-DeepSeek-V2-Lite-Chat": {
        "display_name": "DeepSeek-V2-Lite-Chat",
        "hf_repo": "deepseek-ai/DeepSeek-V2-Lite-Chat",
        "type": "hf",
        "expected_vocab": 100002,
    },
}

GPT_FAMILY = {
    "gpt-4o": {"encoder": "o200k_base", "expected_vocab": 200000},
    "gpt-4": {"encoder": "o200k_base", "expected_vocab": 200000},
    "gpt-3.5-turbo": {"encoder": "cl100k_base", "expected_vocab": 100257},
    "gpt-2": {"encoder": "gpt2", "expected_vocab": 50257},
}

# 테스트 텍스트
KR_TEST = "인공지능은 우리의 삶을 바꾸고 있다."
EN_TEST = "Artificial intelligence changes everything."

# 결과 추적
results = {
    "loaded": [],
    "failed": [],
    "gpt_loaded": [],
    "gpt_failed": [],
    "tokenization_kr": [],
    "tokenization_en": [],
}


def check_model_local(model_key: str, model_info: dict) -> bool:
    """로컬에 모델 디렉토리가 존재하는지 확인"""
    local_path = os.path.join(MODEL_DIR, model_key)
    return os.path.isdir(local_path) and os.path.isfile(os.path.join(local_path, "tokenizer.json"))


def load_hf_tokenizer(model_key: str):
    """HuggingFace 토크나이저 로드"""
    local_path = os.path.join(MODEL_DIR, model_key)
    try:
        tok = AutoTokenizer.from_pretrained(local_path, use_fast=True, local_files_only=True)
        return tok
    except Exception:
        try:
            tok = AutoTokenizer.from_pretrained(local_path, use_fast=False, local_files_only=True)
            return tok
        except Exception:
            return None


def get_vocab_size(tokenizer) -> int:
    """토크나이저의 vocab size 반환"""
    if hasattr(tokenizer, 'vocab') and tokenizer.vocab:
        return len(tokenizer.vocab)
    if hasattr(tokenizer, 'get_vocab'):
        return len(tokenizer.get_vocab())
    return -1


def count_tokens(tokenizer, text: str) -> tuple[int, list[str]]:
    """텍스트 토큰화하고 토큰 수와 토큰 문자열 리스트 반환"""
    try:
        encoding = tokenizer(text, return_offsets_mapping=True)
        tokens = []
        for tid, (s, e) in zip(encoding.input_ids, encoding.offset_mapping):
            if s == 0 and e == 0:
                continue
            tokens.append(text[s:e])
        return len(tokens), tokens
    except Exception:
        try:
            encoding = tokenizer(text, add_special_tokens=False)
            tokens = tokenizer.convert_ids_to_tokens(encoding.input_ids)
            if not tokens:
                # 바이트 fallback
                encoded = text.encode("utf-8")
                return len(encoded), [chr(b) for b in encoded]
            token_strs = []
            for t in tokens:
                ts = t.replace("▁", " ") if isinstance(t, str) else t.decode("utf-8", errors="replace")
                token_strs.append(ts)
            return len(token_strs), token_strs
        except Exception:
            encoded = text.encode("utf-8")
            return len(encoded), [chr(b) for b in encoded]


def check_gpt_encoder(encoder_name: str) -> tuple[bool, any]:
    """tiktoken 인코더 로드 확인"""
    try:
        enc = tiktoken.get_encoding(encoder_name)
        return True, enc
    except Exception:
        return False, None


def main():
    print("=" * 70)
    print("LLM 토크나이저 모델 검증")
    print("=" * 70)
    print()

    # ── 1. HuggingFace 모델 검증 ──
    print("[1/4] HuggingFace 오픈웨이트 모델 검증")
    print("-" * 50)

    for model_key, model_info in MODELS.items():
        display_name = model_info["display_name"]
        local_exists = check_model_local(model_key, model_info)
        tokenizer = None
        vocab_size = -1
        kr_tokens = 0
        en_tokens = 0
        kr_sample = []
        en_sample = []
        status = "❌"

        if local_exists:
            tokenizer = load_hf_tokenizer(model_key)
            if tokenizer is not None:
                vocab_size = get_vocab_size(tokenizer)
                expected = model_info.get("expected_vocab", -1)
                vocab_ok = expected == -1 or vocab_size == expected

                kr_tokens, kr_sample = count_tokens(tokenizer, KR_TEST)
                en_tokens, en_sample = count_tokens(tokenizer, EN_TEST)

                status = "✅"
                results["loaded"].append(model_key)
                results["tokenization_kr"].append((display_name, kr_tokens, kr_sample[:5]))
                results["tokenization_en"].append((display_name, en_tokens, en_sample[:5]))
            else:
                status = "⚠️"
                results["failed"].append(model_key)
        else:
            status = "❌"
            results["failed"].append(model_key)

        # 출력
        kr_sample_str = ", ".join(f'"{t}"' for t in kr_sample) if kr_sample else "(없음)"
        en_sample_str = ", ".join(f'"{t}"' for t in en_sample) if en_sample else "(없음)"

        print(f"  {status} {display_name}")
        print(f"      로컬: {'✅' if local_exists else '❌'} | vocab: {vocab_size:,} | "
              f"KR: {kr_tokens}토큰 | EN: {en_tokens}토큰")
        if kr_sample:
            print(f"      KR 샘플: {kr_sample_str}")
        if en_sample:
            print(f"      EN 샘플: {en_sample_str}")
        print()

    # ── 2. GPT 계열 검증 ──
    print("[2/4] GPT 계열 (tiktoken) 검증")
    print("-" * 50)

    for model_name, info in GPT_FAMILY.items():
        encoder_name = info["encoder"]
        ok, encoder = check_gpt_encoder(encoder_name)

        if ok:
            kr_tokens, kr_sample = count_tokens(encoder, KR_TEST)
            en_tokens, en_sample = count_tokens(encoder, EN_TEST)
            status = "✅"
            results["gpt_loaded"].append(model_name)
            results["tokenization_kr"].append((model_name, kr_tokens, kr_sample[:5]))
            results["tokenization_en"].append((model_name, en_tokens, en_sample[:5]))
        else:
            status = "❌"
            results["gpt_failed"].append(model_name)

        en_sample_str = ", ".join(f'"{t}"' for t in en_sample[:5]) if en_sample else "(없음)"
        kr_sample_str = ", ".join(f'"{t}"' for t in kr_sample[:5]) if kr_sample else "(없음)"

        print(f"  {status} {model_name} ({encoder_name})")
        print(f"      vocab: {info['expected_vocab']:,} | KR: {kr_tokens}토큰 | EN: {en_tokens}토큰")
        if en_sample:
            print(f"      EN 샘플: {en_sample_str}")
        print()

    # ── 3. 요약 ──
    print("[3/4] 요약")
    print("-" * 50)
    print(f"  HF 모델 로드: {len(results['loaded'])}/{len(MODELS)} 성공")
    print(f"  GPT 계열 로드: {len(results['gpt_loaded'])}/{len(GPT_FAMILY)} 성공")

    if results["failed"]:
        print(f"\n  ❌ 실패한 HF 모델:")
        for key in results["failed"]:
            print(f"     - {MODELS[key]['display_name']}")

    if results["gpt_failed"]:
        print(f"\n  ❌ 실패한 GPT 모델:")
        for name in results["gpt_failed"]:
            print(f"     - {name}")

    # ── 4. 한글 vs 영어 토큰 수 비교 ──
    print("\n[4/4] 한글 vs 영어 토큰 수 비교")
    print("-" * 50)
    print(f"  테스트 문장 (한글): \"{KR_TEST}\" ({len(KR_TEST)}자)")
    print(f"  테스트 문장 (영문): \"{EN_TEST}\" ({len(EN_TEST)}자)")
    print()

    # 토큰 수를 모델명 순으로 정렬하여 비교
    all_results = []
    for name, count, _ in results["tokenization_kr"]:
        all_results.append((name, "KR", count))
    for name, count, _ in results["tokenization_en"]:
        all_results.append((name, "EN", count))

    # 한글/영문 결과를 모델별로 묶어 표시
    kr_by_model = {r[0]: r[1] for r in results["tokenization_kr"]}
    en_by_model = {r[0]: r[1] for r in results["tokenization_en"]}

    all_model_names = sorted(set(list(kr_by_model.keys()) + list(en_by_model.keys())))
    print(f"  {'모델':<20} {'한글 토큰':>12} {'영문 토큰':>12} {'차이':>8}")
    print(f"  {'-' * 20} {'-' * 12} {'-' * 12} {'-' * 8}")
    for name in all_model_names:
        kr = kr_by_model.get(name, "-")
        en = en_by_model.get(name, "-")
        if kr != "-" and en != "-":
            diff = kr - en
            diff_str = f"{diff:+d}"
        else:
            diff_str = "-"
        kr_str = f"{kr}" if kr != "-" else "-"
        en_str = f"{en}" if en != "-" else "-"
        print(f"  {name:<20} {kr_str:>12} {en_str:>12} {diff_str:>8}")

    print()
    print("=" * 70)
    print("검증 완료!")
    print("=" * 70)


if __name__ == "__main__":
    main()
