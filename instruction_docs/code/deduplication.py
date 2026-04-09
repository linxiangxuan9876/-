"""
Q&A 查重服务模块
使用 FuzzyWuzzy 进行文本相似度检测
"""
from typing import List, Tuple, Optional
from fuzzywuzzy import fuzz


DUPLICATE_THRESHOLD = 0.85  # 85% 相似度阈值
HIGH_RISK_THRESHOLD = 0.95  # 高风险阈值


def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度

    Args:
        text1: 文本1
        text2: 文本2

    Returns:
        相似度分数 (0.0 - 1.0)
    """
    t1 = text1.lower().strip()
    t2 = text2.lower().strip()

    # 精确匹配
    if t1 == t2:
        return 1.0

    # 模糊匹配
    ratio = fuzz.ratio(t1, t2) / 100.0
    partial_ratio = fuzz.partial_ratio(t1, t2) / 100.0

    # 综合评分（可调整权重）
    score = ratio * 0.6 + partial_ratio * 0.4

    return score


def check_similarity(text1: str, text2: str, threshold: float = DUPLICATE_THRESHOLD) -> bool:
    """
    检查两个文本是否相似

    Args:
        text1: 文本1
        text2: 文本2
        threshold: 相似度阈值

    Returns:
        True if similar, False otherwise
    """
    return calculate_similarity(text1, text2) >= threshold


def find_duplicates(
    texts: List[str],
    threshold: float = DUPLICATE_THRESHOLD
) -> List[Tuple[int, int, float]]:
    """
    在文本列表中查找重复对

    Args:
        texts: 文本列表
        threshold: 相似度阈值

    Returns:
        [(index1, index2, similarity), ...]
    """
    duplicates = []

    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            similarity = calculate_similarity(texts[i], texts[j])
            if similarity >= threshold:
                duplicates.append((i, j, similarity))

    return duplicates


def check_duplicates_in_database(
    new_question: str,
    existing_questions: List[Tuple[int, str]],
    threshold: float = DUPLICATE_THRESHOLD
) -> List[dict]:
    """
    检查新问题是否与数据库中现有问题重复

    Args:
        new_question: 新问题
        existing_questions: [(id, question), ...]
        threshold: 相似度阈值

    Returns:
        [{"id": xxx, "question": "xxx", "similarity": 0.92}, ...]
    """
    results = []

    for qa_id, question in existing_questions:
        similarity = calculate_similarity(new_question, question)
        if similarity >= threshold:
            results.append({
                "id": qa_id,
                "question": question,
                "similarity": similarity,
                "risk_level": "high" if similarity >= HIGH_RISK_THRESHOLD else "medium"
            })

    # 按相似度降序排序
    results.sort(key=lambda x: x["similarity"], reverse=True)

    return results


def batch_check_duplicates(
    questions: List[str],
    threshold: float = DUPLICATE_THRESHOLD
) -> dict:
    """
    批量检查问题重复

    Args:
        questions: 问题列表
        threshold: 相似度阈值

    Returns:
        {
            "has_duplicates": bool,
            "duplicates": [(index1, index2, similarity), ...],
            "duplicate_groups": [[index1, index2, index3], ...]
        }
    """
    duplicates = find_duplicates(questions, threshold)

    # 找出所有重复组（连通分量）
    visited = set()
    duplicate_groups = []

    for i, j, sim in duplicates:
        if i not in visited and j not in visited:
            group = [i, j]
            visited.add(i)
            visited.add(j)

            # 查找组内所有相关索引
            changed = True
            while changed:
                changed = False
                for idx1, idx2, _ in duplicates:
                    if idx1 in group and idx2 not in group:
                        group.append(idx2)
                        visited.add(idx2)
                        changed = True
                    elif idx2 in group and idx1 not in group:
                        group.append(idx1)
                        visited.add(idx1)
                        changed = True

            duplicate_groups.append(sorted(group))

    return {
        "has_duplicates": len(duplicates) > 0,
        "duplicates": duplicates,
        "duplicate_groups": duplicate_groups
    }


def get_similarity_level(similarity: float) -> str:
    """获取相似度等级描述"""
    if similarity >= 0.95:
        return "high"
    elif similarity >= 0.85:
        return "medium"
    else:
        return "low"
