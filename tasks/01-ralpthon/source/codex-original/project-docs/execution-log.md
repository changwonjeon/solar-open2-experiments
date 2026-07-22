
### 🔍 트러블슈팅 노트 (2026-07-17)

**1. claude-upstage 파서 문제**
- `run-ralph-solar.sh`에서 `exec claude-upstage --allow-dangerously-skip-permissions` 호출 시, `claude-upstage`의 `parse_flags` 함수가 알 수 없는 옵션으로 간주하여 즉시 `exit 1`
- **시도된 해결**: `run-ralph-solar.sh`를 수정하여 `ANTHROPIC_*` 환경변수를 직접 설정하고 `exec claude --allow-dangerously-skip-permissions` 호출. **사용자가 "claude CLI 직접 실행은 허용하지 않음" 제약 조건을 제시하여 거부됨**
- **해결**: `run-ralph-solar.sh`를 `exec claude-upstage` (인자 없음, 인터랙티브 REPL 진입)으로 복원. `start-ralph-solar.sh`와 `ralph-deadline-watchdog.sh`가 `tmux send-keys`로 초기 `$ralph` 프롬프트와 권한 승인(`y`)을 자동 주입. (Question Mode)

**2. WSL2 환경 호환성 문제**
- `/usr/bin/caffeinate` (macOS 전용) 제거
- `$ROOT` 경로 계산 수정: `ROOT="${SCRIPT_DIR:h:h}"` → `ROOT="${SCRIPT_DIR:h:h:h}"` (WSL2 환경 및 프로젝트 루트에 맞게)
- `tmux` 세션 이름은 기존 `ralphthon-loop`, `ralpthon-deadline` 유지

**3. 시간 기준 문제**
- 초기 Watchdog가 2026-07-12 절대 시간 기준이라 7/17 실행 시 `delta` 음수 → 즉시 종료
- **해결**: `start_time=$(date +%s)`로 **스크립트 실행 순간의 상대 시간**을 기준으로 3시간 측정. 루프 진입 전 1회 캡처하여 고정.

**4. Git Preflight 검사 실패**
- `git status --porcelain`이 `docs/experiments/ralphthon/`, `src/scripts/ralpthon/`를 untracked 파일로 감지하여 `exit 4`
- **해결**: `git status --porcelain --untracked-files=no`로 수정하여 tracked 파일만 검사

**5. 2026-07-17 16:47 KST 검증 결과**
- `start-ralph-solar.sh START-RALPH` 실행 후 `ralphthon-loop` tmux 세션 활성 확인
- `claude-upstage` 실행 로그 캡처 성공 (`☀ Solar Open2 × Claude Code`, `Model: solar-open2`)
- 테스트 워치독(10s/1s/2s 모드) 실행으로 무활동 감지 및 프롬프트 재전송 입증 완료

