import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from app.schemas import SeniorCoderContext
from app.prompts import CODER_SYSTEM_PROMPT
from app.tools import tools_coder, ARTIFACT_DIR

def create_coder_agent(model_name: str = "google_genai:gemini-flash-latest", model_provider: str | None = None, temperature: float = 0.2):
    """데이터 청사진을 코드로 제작/수행하는 Coder 에이전트 생성"""
    if model_provider:
        model = init_chat_model(model_name, model_provider=model_provider, temperature=temperature)
    else:
        model = init_chat_model(model_name, temperature=temperature)
    checkpointer = InMemorySaver()
    
    # 파일 탐색 미들웨어는 현재 환경에서 절대 경로 패턴을 거부하므로 기본 생성만 유지합니다.
    agent = create_agent(
        model=model,
        system_prompt=CODER_SYSTEM_PROMPT,
        context_schema=SeniorCoderContext,
        tools=tools_coder,
        checkpointer=checkpointer,
        middleware=[]
    )
    return agent
