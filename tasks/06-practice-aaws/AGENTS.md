# 06-practice-aaws 태스크 로컬 규칙

## 실습 진행 중 파일 수정
- ✅ 실습 진행 중에는 `aaws/` 내 원본 파일 수정 허용 (Source 불변성 예외)
- ✅ `aaws/Mission.md` 등 실습 가이드 문서 수정 허용
- ⚠️ submodule 업데이트 시 로컬 수정 내용이 덮어씌워질 수 있음 — 중요 수정은 별도 관리

## 보호 범위
- `docs/`, `data/` 디렉토리의 OKF 포맷 준수 (`docs/` 내 마크다운)
- `output/` — solar-open2 사용한 경우에만 산출물 저장/반영
- `aaws/` — git submodule로 관리, 로컬 수정 허용
- `aaws/.env` — API 키 포함, git 추적 대상에서 제외
- `git add`/`commit`/`push`는 사용자 승인 후 실행

## 하위 태스크
- 06-01: Jupyter Notebook 실습 (01~05 노트북)
- 06-02: Mission.md 단계별 미션 수행
- 06-03: 시나리오 자동 평가 (Sequential / Supervisor)
- 06-04: 2일차 자율 개선 프로젝트
