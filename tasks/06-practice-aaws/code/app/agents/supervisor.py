import sys
import os
import json

from langchain.tools import tool, ToolRuntime
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

# Load environment
from dotenv import load_dotenv
load_dotenv(override=True)

# 워커 에이전트들 임포트 — app/ 패키지 기반
from app.agents.navigator import create_navigator_agent
from app.agents.coder import create_coder_agent
from app.schemas import NavigatorContext, SeniorCoderContext

# 추가 유틸리티 툴스 (Tool Factory)
from app.tools import tools_supervisor

# 서빙용 프롬프트
from app.prompts import SUPERVISOR_SYSTEM_PROMPT

from browser_use import Agent, Browser, ChatGoogle

# 하위 에이전트는 전역에서 한 번만 생성하고 재사용하여 메모리/맥락(Checkpointer)을 유지합니다.

# =========================================================
# 1. 하위 에이전트 인스턴스 전역 생성 (상태 유지용)
# =========================================================
GLOBAL_NAVIGATOR_AGENT = None
GLOBAL_CODER_AGENT = None


def refresh_worker_agents(
    navigator_model_name: str = "google_genai:gemini-2.5-pro",
    navigator_model_provider: str | None = None,
    coder_model_name: str = "google_genai:gemini-flash-latest",
    coder_model_provider: str | None = None,
):
    """Supervisor가 사용할 Navigator/Coder worker 에이전트를 재생성합니다."""
    global GLOBAL_NAVIGATOR_AGENT, GLOBAL_CODER_AGENT
    GLOBAL_NAVIGATOR_AGENT = create_navigator_agent(
        model_name=navigator_model_name,
        model_provider=navigator_model_provider,
    )
    GLOBAL_CODER_AGENT = create_coder_agent(
        model_name=coder_model_name,
        model_provider=coder_model_provider,
    )
    return GLOBAL_NAVIGATOR_AGENT, GLOBAL_CODER_AGENT

# =========================================================
# 2. 분리된(Context Isolated) Handoff 도구 (Agents as Tools 패턴)
# =========================================================

@tool(parse_docstring=True)
async def chat_to_navigator(request: str, runtime: ToolRuntime, config: RunnableConfig, url: str = "", mode: str = "blueprint") -> str:
    """웹사이트의 구조를 분석하여 데이터를 추출할 수 있는 Blueprint(설계도)를 만들기 위해 웹탐색 전문가인 네비게이터와 대화합니다.
    사용자가 특정 크롤링을 원하거나 질문/인사가 있을 때 가장 먼저 이 도구를 사용하여 네비게이터에게 지시하세요.
    
    Args:
        request: 네비게이터에게 전달할 지시사항, 목표, 질문, 인사말 등
        url: 분석할 웹페이지의 기본 URL (반드시 http/https 포함). 단순 질문/대화이면 빈 문자열로.
        mode: 실행 모드. 청사진 생성이면 'blueprint', 단순 자연어 대화/질문/탐색이면 'chat'
    """

    prompt = f"Request: {request}\nTarget URL: {url}\nMode: {mode}"
    print(f"\n👨‍💼 [Supervisor] Navigator와 대화 중...(Mode: {mode}, URL: {url or '없음'})")

    # Runtime Context용 공유 브라우저 인스턴스 생성
    browser_instance = Browser(
        headless=False,
        disable_security=True,
        keep_alive=True,
    )

    ctx = NavigatorContext(shared_browser=browser_instance, response_mode=mode)
    
    try:
        # FastAPI/UI로 이벤트를 전달하기 위해 원본 config(callbacks 포함)를 그대로 전달해야 합니다.
        inner_config = config.copy() if config else {}
        inner_config["configurable"] = inner_config.get("configurable", {}).copy()
        inner_config["configurable"]["thread_id"] = config.get("configurable", {}).get("thread_id", "default_thread")
        
        result = await GLOBAL_NAVIGATOR_AGENT.ainvoke(
            {"messages": [("user", prompt)]},
            context=ctx,
            config=inner_config
        )
        return result["messages"][-1].content
    finally:
        if browser_instance:
            await browser_instance.stop()
        

@tool(parse_docstring=True)
async def chat_to_coder(task_description: str, runtime: ToolRuntime, config: RunnableConfig, blueprint_info: str = "") -> str:
    """Coder에게 파이썬 코드 작성, 실행, 디버깅 등의 작업을 지시할 때 사용합니다.
    크롤링 스크립트 기반 코딩 작업을 지시할 때는 Navigator가 생성한 Blueprint를 함께 전달하세요.
    
    Args:
        task_description: 작성할 스크립트의 코드 구현 목표 및 구체적 요구사항
        blueprint_info: Navigator가 찾아낸 렌더링 방식 및 대상 사이트 구조 정보(Blueprint). 불필요하면 빈 문자열.
    """
    
    prompt = f"다음 [Task]를 수행하세요.\n\n[Task]\n{task_description}"
    if blueprint_info:
        prompt += f"\n\n[Blueprint]\n{blueprint_info}"
        
    print(f"\n👨‍💼 [Supervisor] Coder와 대화 중...")
    
    inner_config = config.copy() if config else {}
    inner_config["configurable"] = inner_config.get("configurable", {}).copy()
    inner_config["configurable"]["thread_id"] = config.get("configurable", {}).get("thread_id", "default_thread")
    
    result = await GLOBAL_CODER_AGENT.ainvoke(
        {"messages": [("user", prompt)]},
        context=SeniorCoderContext(),
        config=inner_config
    )
    return result["messages"][-1].content


# =========================================================
# 3. Supervisor Agent 구성
# =========================================================

def create_supervisor_agent(
    model_name: str = "google_genai:gemini-2.5-pro",
    model_provider: str | None = None,
    temperature: float = 0.1,
    project_name: str | None = None,
    navigator_model_name: str | None = None,
    navigator_model_provider: str | None = None,
    coder_model_name: str | None = None,
    coder_model_provider: str | None = None,
):
    """역할별 모델을 명시적으로 주입할 수 있는 Supervisor 에이전트를 생성합니다."""
    if project_name:
        os.environ["LANGSMITH_PROJECT"] = project_name

    refresh_worker_agents(
        navigator_model_name=navigator_model_name or model_name,
        navigator_model_provider=(
            navigator_model_provider
            if navigator_model_name is not None
            else model_provider
        ),
        coder_model_name=coder_model_name or model_name,
        coder_model_provider=(
            coder_model_provider if coder_model_name is not None else model_provider
        ),
    )

    if model_provider:
        supervisor_model = init_chat_model(model_name, model_provider=model_provider, temperature=temperature)
    else:
        supervisor_model = init_chat_model(model_name, temperature=temperature)

    supervisor_checkpointer = InMemorySaver()
    supervisor_agent = create_agent(
        model=supervisor_model,
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        tools=[chat_to_navigator, chat_to_coder] + tools_supervisor,
        checkpointer=supervisor_checkpointer,
        name="supervisor_agent"
    )
    return supervisor_agent


# app/server.py에서 agent_executor로 접근할 수 있게 alias 지정
agent_executor = create_supervisor_agent()
