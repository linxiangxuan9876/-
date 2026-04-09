"""
AI 分类服务模块
调用 OpenAI API 进行 Q&A 分类
使用 langchain_openai 库
"""
import json
import re
from typing import Optional
from app.core.config import settings


CATEGORIES = ["保修政策", "保养维护", "故障诊断", "配件更换", "服务预约", "门店活动"]


CLASSIFY_PROMPT = """
请为以下 Q&A 内容分类：

问题：{question}
答案：{answer}

可选分类：{categories}

要求：
1. 只选择一个最匹配的主分类
2. 生成一个简洁的子分类（2-4个字）
3. 子分类应具体描述问题类型

返回 JSON 格式：
{{"main_category": "主分类", "sub_category": "子分类"}}
"""


async def classify_qa(question: str, answer: str) -> Optional[dict]:
    """
    使用 AI 对 Q&A 进行分类

    Args:
        question: 问题内容
        answer: 答案内容

    Returns:
        {"main_category": "主分类", "sub_category": "子分类"} 或 None
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key not configured")

    prompt = CLASSIFY_PROMPT.format(
        question=question,
        answer=answer,
        categories="、".join(CATEGORIES)
    )

    try:
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage

        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0
        )

        messages = [HumanMessage(content=prompt)]
        response = await llm.agenerate([messages])

        content = response.generations[0][0].text.strip()
        return parse_classify_response(content)

    except Exception as e:
        print(f"分类失败: {e}")
        return None


def parse_classify_response(content: str) -> Optional[dict]:
    """
    解析分类响应

    Args:
        content: API 返回的原始内容

    Returns:
        分类结果字典或 None
    """
    try:
        # 尝试提取 JSON
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            result = json.loads(match.group())

            # 验证分类是否有效
            if result.get("main_category") in CATEGORIES:
                return result

            # 如果分类无效，尝试匹配部分
            for cat in CATEGORIES:
                if cat in result.get("main_category", ""):
                    result["main_category"] = cat
                    return result

    except json.JSONDecodeError:
        pass

    return None


async def batch_classify_qa(qa_list: list[dict]) -> list[dict]:
    """
    批量分类 Q&A

    Args:
        qa_list: [{"question": "...", "answer": "..."}, ...]

    Returns:
    [{"question": "...", "answer": "...", "main_category": "...", "sub_category": "..."}, ...]
    """
    results = []

    for qa in qa_list:
        category = await classify_qa(qa["question"], qa["answer"])

        if category:
            results.append({
                **qa,
                **category,
                "classification_confidence": "high"
            })
        else:
            # 分类失败时使用默认值
            results.append({
                **qa,
                "main_category": "其他",
                "sub_category": "未分类",
                "classification_confidence": "low"
            })

    return results


async def validate_category(category: str) -> bool:
    """验证分类是否有效"""
    return category in CATEGORIES


def get_default_category() -> dict:
    """获取默认分类"""
    return {
        "main_category": "其他",
        "sub_category": "未分类"
    }
