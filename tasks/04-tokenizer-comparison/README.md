# Tokenizer Comparison

여러 오픈웨이트 모델의 토크나이저 결과를 비교하는 태스크 작업공간입니다.

## 구조

- `source/original/`: 원본 애플리케이션, 검증 스크립트, 토크나이저 자산
- `docs/tokenizer-comparison/`: OKF Wiki 문서
- `output/`: 생성 산출물
- `AGENTS.md`, `CLAUDE.md`: 태스크 로컬 규칙

`source/original/` 내용은 읽기 전용으로 유지합니다.

## 실행 방법 (uv)

이 프로젝트는 `uv` 기반 프로젝트입니다. `source/original/pyproject.toml`에 의존성이 선언되어 있습니다.

### 1. 환경 설정 (처음 한 번만)

```bash
cd tasks/04-tokenizer-comparison/source/original

# 가상환경 생성 + 의존성 설치
uv sync
```

> `uv sync`는 `pyproject.toml`의 의존성을 읽고 가상환경과 패키지를 한 번에 구성합니다.

### 2. 토큰 측정 CLI 실행

```bash
uv run python verify_models.py
```

> 한글·영문 테스트 문장에 대해 14개 모델의 토큰 수를 비교해 표로 출력합니다.

### 3. 대화형 Streamlit 앱 실행

```bash
uv run streamlit run app.py
```

브라우저가 `http://localhost:8501`로 열리며, 텍스트를 입력해 모델별 토큰 분할을 시각적으로 비교할 수 있습니다.
