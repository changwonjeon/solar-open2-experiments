import os
import sys
import asyncio
import argparse
from dotenv import load_dotenv

# Project Root Setup
project_root = os.getenv("PROJECT_ROOT", os.getcwd())
if not os.path.exists(os.path.join(project_root, "app")):
    current = os.getcwd()
    for _ in range(5):
        if os.path.exists(os.path.join(current, "app")):
            project_root = current
            break
        current = os.path.dirname(current)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment
load_dotenv(override=True)

# LangSmith tracing for all runs
os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("AAWS_MODEL_MODE", "gemini")

from app.agents.supervisor import create_supervisor_agent
from tests.config_loader import load_target_scenarios
from tests.test_helpers import (
    setup_scenario_context,
    stream_agent_execution,
    evaluate_and_log
)


def parse_args():
    parser = argparse.ArgumentParser(description="Run AAWS supervisor scenarios")
    parser.add_argument("--model-mode", choices=["gemini", "upstage", "both"], default="gemini")
    return parser.parse_args()


def get_langsmith_project(model_mode: str) -> str:
    """모델별 LangSmith 프로젝트명을 환경변수에서 읽습니다."""
    if model_mode == "upstage":
        return os.getenv(
            "AAWS_LANGSMITH_PROJECT_UPSTAGE",
            "aaws-supervisor-solar-open2",
        )
    return os.getenv(
        "AAWS_LANGSMITH_PROJECT_GEMINI",
        "aaws-supervisor-gemini",
    )


def build_agent_executor(model_mode: str = "gemini"):
    """Gemini 기본 실행 또는 Upstage Solar Open2 실험용 에이전트를 생성합니다."""
    project_name = get_langsmith_project(model_mode)
    # Supervisor와 하위 Navigator/Coder, Evaluator trace를 같은 모델 전용
    # LangSmith 프로젝트에 기록하도록 에이전트 생성 전에 설정합니다.
    os.environ["LANGSMITH_PROJECT"] = project_name

    if model_mode == "upstage":
        os.environ["AAWS_MODEL_MODE"] = "upstage"
        return create_supervisor_agent(
            model_name="solar-open2",
            model_provider="upstage",
            project_name=project_name,
        )
    os.environ["AAWS_MODEL_MODE"] = "gemini"
    return create_supervisor_agent(project_name=project_name)


async def run_scenario(scenario_file: str, model_mode: str = "gemini"):
    """지정된 시나리오 마크다운 파일을 파싱하여 슈퍼바이저 에이전트에 작업을 요청합니다."""
    suffix = "upstage" if model_mode == "upstage" else ""
    scenario, paths = setup_scenario_context(scenario_file, project_root, prefix="sup", suffix=suffix)
    agent_executor = build_agent_executor(model_mode=model_mode)
    langsmith_project = get_langsmith_project(model_mode)
    
    print("\n" + "=" * 80)
    print(f"🚀 [Supervisor] 시나리오 테스트 시작: {os.path.basename(scenario_file)}")
    print(f"🔍 LangSmith 프로젝트: {langsmith_project}")
    print(f"📝 진행 상황은 터미널과 함께 다음 파일에도 저장됩니다: {paths['log_path']}")
    print("=" * 80)
    
    mission_prompt = f"""
    아래에 제공된 마크다운 시나리오 문서를 읽고, 파이프라인(Navigator 및 Coder 등을 활용)을 사용해 수집 목표를 달성하세요. 
    1. Navigator를 통해 URL 탐색 및 Blueprint를 확보하세요.
    2. Coder에게 지시하여 스크래핑 코드를 작성하고 실행하세요.
    3. **매우 중요**: 수집된 데이터는 반드시 다음 경로에 JSON 파일로 저장해야 합니다.
       저장 경로: {paths['json_path']}
    4. 모든 작업이 완료되면 코드 내용과 얻어낸 결과를 최종 텍스트로 요약 분석하여 보고하세요.
    
    [대상 사이트 정보]
    - 사이트명: {scenario.site_name}
    - 기준 URL: {scenario.target_url}
    
    [시나리오 문서]
    {scenario.prompt}
    """

    print("⏳ 에이전트 수행 중 (상당한 시간이 소요될 수 있습니다)...")
    
    try:
        # 1. 에이전트 스트리밍 실행 (이벤트 처리 및 로그 기록 전담)
        final_message = await stream_agent_execution(
            agent_executor, mission_prompt, paths['log_path']
        )
        
        # 2. Evaluator 평가 및 채점 리포트 출력
        await evaluate_and_log(
            scenario, paths['json_path'], final_message, paths['log_path']
        )
        
    except Exception as e:
        print(f"\n❌ 시나리오 중 오류 발생: {e}")
        with open(paths['log_path'], "a", encoding="utf-8") as f:
            f.write(f"\n❌ 시나리오 중 오류 발생: {e}\n")

async def main():
    args = parse_args()
    artifacts_dir = os.path.join(project_root, "artifacts", "scenarios")

    # 🎯 tests/test_config.yaml 파일에서 실행 대상 시나리오를 로드합니다.
    target_scenarios = load_target_scenarios(project_root)

    scenario_files = []
    for filename in target_scenarios:
        filepath = os.path.join(artifacts_dir, filename)
        if os.path.exists(filepath):
            scenario_files.append(filepath)
        else:
            print(f"⚠️ 파일 없음 (건너뜀): {filepath}")

    if not scenario_files:
        print("❌ 실행할 시나리오 파일이 없습니다. tests/test_config.yaml 설정을 확인하세요.")
        return

    model_modes = ["gemini"] if args.model_mode == "gemini" else ["upstage"] if args.model_mode == "upstage" else ["gemini", "upstage"]

    print(f"총 {len(scenario_files)}개의 시나리오 테스트를 시작합니다.")
    for file_path in scenario_files:
        print(f" - {os.path.basename(file_path)}")

    print("\n" + "="*40)

    for model_mode in model_modes:
        print(f"\n🔁 실행 모드: {model_mode}")
        for file_path in scenario_files:
            await run_scenario(file_path, model_mode=model_mode)

    print("\n🎉 모든 시나리오 테스트 및 평가가 종료되었습니다.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
