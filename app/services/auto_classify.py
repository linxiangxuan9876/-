import json
import re
from typing import Dict, Optional
from fuzzywuzzy import fuzz
from app.services.kb_categories import KB_CATEGORIES

def calculate_similarity(text1: str, text2: str) -> float:
    return fuzz.ratio(text1.lower(), text2.lower()) / 100.0

def find_best_match(question: str, categories: Dict[str, list]) -> tuple[str, str, float]:
    best_main = None
    best_sub = None
    best_score = 0.0

    for main_category, sub_categories in categories.items():
        for sub_category in sub_categories:
            score = calculate_similarity(question, sub_category)
            if score > best_score:
                best_score = score
                best_main = main_category
                best_sub = sub_category

    return best_main, best_sub, best_score

def extract_categories_from_prompt(categories: Dict[str, list]) -> str:
    lines = []
    for main_cat, sub_cats in categories.items():
        lines.append(f"{main_cat}:")
        for sub_cat in sub_cats:
            lines.append(f"  - {sub_cat}")
    return "\n".join(lines)

def keyword_match(question: str) -> Optional[Dict[str, str]]:
    """优先使用关键词匹配 - 按照用户提供的分类表"""
    question_lower = question.lower()

    # ========== 第一优先级：多关键词组合（更精确）==========
    combo_keywords = [
        # (关键词组合, 大类, 小类)
        
        # 门店服务与活动类 - 优先匹配
        (["门店", "电话"], "门店服务与活动", "营业时间与设施"),
        (["门店", "地址"], "门店服务与活动", "营业时间与设施"),
        (["门店", "位置"], "门店服务与活动", "营业时间与设施"),
    ]

    for keywords, main, sub in combo_keywords:
        if all(kw in question_lower for kw in keywords):
            return {"main_category": main, "sub_category": sub}

    # ========== 第二优先级：单关键词匹配 ==========
    # 按照用户提供的分类表
    strong_keywords = {
        # 维修与保养类
        "保养": ("维修与保养", "保养套餐与项目"),
        "维修": ("维修与保养", "维修与工时费用"),
        "配件": ("维修与保养", "配件价格与渠道"),

        # 车辆技术与使用类
        "仪表盘": ("车辆技术与使用", "仪表盘故障报警"),
        "故障": ("车辆技术与使用", "仪表盘故障报警"),
        "报警": ("车辆技术与使用", "仪表盘故障报警"),
        "电池": ("车辆技术与使用", "电池与能耗"),
        "能耗": ("车辆技术与使用", "电池与能耗"),
        "功能": ("车辆技术与使用", "车辆功能使用说明"),
        "使用说明": ("车辆技术与使用", "车辆功能使用说明"),

        # 门店服务与活动类
        "营业时间": ("门店服务与活动", "营业时间与设施"),
        "预约": ("门店服务与活动", "预约与取送车流程"),
        "取送车": ("门店服务与活动", "预约与取送车流程"),
        "优惠券": ("门店服务与活动", "优惠券与活动"),
        "活动": ("门店服务与活动", "优惠券与活动"),

        # 金融保险与理赔类
        "出险": ("金融保险与理赔", "出险与理赔流程"),
        "理赔": ("金融保险与理赔", "出险与理赔流程"),
        "保险": ("金融保险与理赔", "保险购买与续保"),
        "续保": ("金融保险与理赔", "保险购买与续保"),
        "贷款": ("金融保险与理赔", "贷款解压与绿本"),
        "解压": ("金融保险与理赔", "贷款解压与绿本"),
        "绿本": ("金融保险与理赔", "贷款解压与绿本"),
    }

    for keyword, (main, sub) in strong_keywords.items():
        if keyword in question_lower:
            return {"main_category": main, "sub_category": sub}

    return None

async def auto_classify(question: str) -> Dict[str, str]:
    """
    智能分类：关键词匹配 + LLM双重验证
    1. 先用关键词匹配获取候选分类
    2. 再用LLM验证并优化分类结果
    """
    categories_str = extract_categories_from_prompt(KB_CATEGORIES)

    # 第一步：关键词匹配获取候选分类（作为LLM的参考）
    keyword_result = keyword_match(question)
    keyword_hint = ""
    if keyword_result:
        keyword_hint = f"\n关键词匹配提示：该问题可能属于【{keyword_result['main_category']}-{keyword_result['sub_category']}】，请验证并优化。"

    prompt = f"""分析以下汽车4S店的客户问题，将其归入最合适的大类和小类中。

参考分类体系：
{categories_str}
{keyword_hint}

客户问题：{question}

分析要求：
1. 仔细阅读问题，理解客户真实意图
2. 如果提供了关键词匹配提示，请验证该分类是否准确，必要时进行修正
3. 例如"有没有免费午餐"属于门店服务设施相关，应归入"门店服务与活动-营业时间与设施"
4. "保养套餐多少钱"才应归入"维修与保养-保养套餐与项目"
5. 如果无法匹配任何分类，则归入'其他综合问答-其他问题'

请严格返回以下JSON格式（不要包含任何其他内容）：
{{"main_category": "xx", "sub_category": "xx"}}"""

    try:
        classification_result = await call_llm_with_fallback(prompt)
        result = json.loads(classification_result)

        if "main_category" in result and "sub_category" in result:
            main_cat = result["main_category"].strip()
            sub_cat = result["sub_category"].strip()

            if main_cat in KB_CATEGORIES and sub_cat in KB_CATEGORIES[main_cat]:
                return {"main_category": main_cat, "sub_category": sub_cat}

            for main_key, sub_list in KB_CATEGORIES.items():
                if sub_cat in sub_list:
                    return {"main_category": main_key, "sub_category": sub_cat}

        # 如果LLM返回无效，回退到关键词匹配结果
        if keyword_result:
            return keyword_result

        # 最后尝试模糊匹配
        best_main, best_sub, best_score = find_best_match(question, KB_CATEGORIES)
        if best_score > 0.8:
            return {"main_category": best_main, "sub_category": best_sub}

        return {"main_category": "其他综合问答", "sub_category": "其他问题"}

    except json.JSONDecodeError:
        if keyword_result:
            return keyword_result
        best_main, best_sub, best_score = find_best_match(question, KB_CATEGORIES)
        if best_score > 0.8:
            return {"main_category": best_main, "sub_category": best_sub}
        return {"main_category": "其他综合问答", "sub_category": "其他问题"}
    except Exception:
        if keyword_result:
            return keyword_result
        best_main, best_sub, best_score = find_best_match(question, KB_CATEGORIES)
        if best_score > 0.8:
            return {"main_category": best_main, "sub_category": best_sub}
        return {"main_category": "其他综合问答", "sub_category": "其他问题"}

async def call_llm_with_fallback(prompt: str) -> str:
    try:
        from app.services.llm_service import call_openai_llm
        return await call_openai_llm(prompt)
    except Exception:
        return mock_llm_response(prompt)

def mock_llm_response(prompt: str) -> str:
    """模拟LLM响应 - 使用与keyword_match相同的逻辑"""
    prompt_lower = prompt.lower()

    # 第一优先级：组合关键词 - 门店类优先
    combo_keywords = [
        (["门店", "电话"], "门店服务与活动", "营业时间与设施"),
        (["门店", "地址"], "门店服务与活动", "营业时间与设施"),
        (["门店", "位置"], "门店服务与活动", "营业时间与设施"),
    ]

    for keywords, main, sub in combo_keywords:
        if all(kw in prompt_lower for kw in keywords):
            return json.dumps({"main_category": main, "sub_category": sub})

    # 第二优先级：单关键词匹配 - 按照用户提供的分类表
    strong_keywords = {
        # 维修与保养类
        "保养": ("维修与保养", "保养套餐与项目"),
        "维修": ("维修与保养", "维修与工时费用"),
        "配件": ("维修与保养", "配件价格与渠道"),

        # 车辆技术与使用类
        "仪表盘": ("车辆技术与使用", "仪表盘故障报警"),
        "故障": ("车辆技术与使用", "仪表盘故障报警"),
        "报警": ("车辆技术与使用", "仪表盘故障报警"),
        "电池": ("车辆技术与使用", "电池与能耗"),
        "能耗": ("车辆技术与使用", "电池与能耗"),
        "功能": ("车辆技术与使用", "车辆功能使用说明"),
        "使用说明": ("车辆技术与使用", "车辆功能使用说明"),

        # 门店服务与活动类
        "营业时间": ("门店服务与活动", "营业时间与设施"),
        "预约": ("门店服务与活动", "预约与取送车流程"),
        "取送车": ("门店服务与活动", "预约与取送车流程"),
        "优惠券": ("门店服务与活动", "优惠券与活动"),
        "活动": ("门店服务与活动", "优惠券与活动"),

        # 金融保险与理赔类
        "出险": ("金融保险与理赔", "出险与理赔流程"),
        "理赔": ("金融保险与理赔", "出险与理赔流程"),
        "保险": ("金融保险与理赔", "保险购买与续保"),
        "续保": ("金融保险与理赔", "保险购买与续保"),
        "贷款": ("金融保险与理赔", "贷款解压与绿本"),
        "解压": ("金融保险与理赔", "贷款解压与绿本"),
        "绿本": ("金融保险与理赔", "贷款解压与绿本"),
    }

    for keyword, (main, sub) in strong_keywords.items():
        if keyword in prompt_lower:
            return json.dumps({"main_category": main, "sub_category": sub})

    return json.dumps({"main_category": "其他综合问答", "sub_category": "其他问题"})
