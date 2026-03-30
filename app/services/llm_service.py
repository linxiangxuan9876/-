import os
from app.core.config import settings

async def call_openai_llm(prompt: str) -> str:
    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key not configured")

    try:
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage

        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=0
        )

        messages = [HumanMessage(content=prompt)]
        response = await llm.agenerate([messages])

        return response.generations[0][0].text.strip()

    except Exception as e:
        raise RuntimeError(f"Failed to call OpenAI API: {str(e)}")
