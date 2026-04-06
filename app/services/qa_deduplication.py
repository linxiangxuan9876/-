"""
QA 查重服务
使用文本相似度算法检测重复或相似的 Q&A
"""
from typing import List, Dict, Optional, Tuple
from fuzzywuzzy import fuzz
from sqlalchemy.orm import Session
from app.models.qa_item import QA_Item, QAStatus


class QADeduplicationService:
    """QA 查重服务"""
    
    # 相似度阈值（百分比）
    SIMILARITY_THRESHOLD = 85  # 85% 相似度认为重复
    
    @classmethod
    def calculate_similarity(cls, text1: str, text2: str) -> int:
        """
        计算两个文本的相似度
        返回 0-100 的相似度分数
        """
        # 使用多种算法计算相似度，取最高值
        # 1. 简单比率（完全匹配）
        ratio = fuzz.ratio(text1, text2)
        
        # 2. 部分比率（部分匹配）
        partial_ratio = fuzz.partial_ratio(text1, text2)
        
        # 3. Token 排序比率（忽略顺序）
        token_sort_ratio = fuzz.token_sort_ratio(text1, text2)
        
        # 4. Token 集合比率（忽略重复和顺序）
        token_set_ratio = fuzz.token_set_ratio(text1, text2)
        
        # 返回最高相似度
        return max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)
    
    @classmethod
    def check_duplicate_question(
        cls,
        question: str,
        answer: str,
        db: Session,
        exclude_id: Optional[int] = None,
        threshold: Optional[int] = None
    ) -> Tuple[bool, List[Dict]]:
        """
        检查问题是否重复
        
        Args:
            question: 要检查的问题
            answer: 答案（用于辅助判断）
            db: 数据库会话
            exclude_id: 排除的 QA ID（用于编辑场景）
            threshold: 相似度阈值，默认使用类属性
            
        Returns:
            (是否重复，相似 QA 列表)
        """
        if threshold is None:
            threshold = cls.SIMILARITY_THRESHOLD
        
        # 查询所有已发布的 QA（排除已删除的）
        query = db.query(QA_Item).filter(
            QA_Item.status == QAStatus.published,
            QA_Item.is_deleted == False
        )
        
        if exclude_id:
            query = query.filter(QA_Item.id != exclude_id)
        
        published_qas = query.all()
        
        similar_qas = []
        
        for qa in published_qas:
            # 计算问题相似度
            question_similarity = cls.calculate_similarity(question, qa.question)
            
            # 如果问题相似度超过阈值，认为是重复
            if question_similarity >= threshold:
                similar_qas.append({
                    "id": qa.id,
                    "question": qa.question,
                    "answer": qa.answer,
                    "similarity": question_similarity,
                    "category": f"{qa.main_category} - {qa.sub_category}"
                })
                continue
            
            # 如果问题相似度在 60-85 之间，再检查答案相似度
            if question_similarity >= 60:
                answer_similarity = cls.calculate_similarity(answer, qa.answer)
                if answer_similarity >= threshold:
                    similar_qas.append({
                        "id": qa.id,
                        "question": qa.question,
                        "answer": qa.answer,
                        "similarity": max(question_similarity, answer_similarity),
                        "category": f"{qa.main_category} - {qa.sub_category}"
                    })
        
        # 按相似度排序
        similar_qas.sort(key=lambda x: x["similarity"], reverse=True)
        
        return len(similar_qas) > 0, similar_qas
    
    @classmethod
    def check_duplicate_for_document_qa(
        cls,
        question: str,
        answer: str,
        db: Session,
        threshold: Optional[int] = None
    ) -> Tuple[bool, List[Dict]]:
        """
        检查文档提取的 QA 是否重复
        与 check_duplicate_question 类似，但用于文档 QA 场景
        """
        return cls.check_duplicate_question(question, answer, db, threshold=threshold)
    
    @classmethod
    def get_similar_questions(
        cls,
        question: str,
        db: Session,
        limit: int = 5
    ) -> List[Dict]:
        """
        获取与给定问题最相似的问题列表
        用于智能提示和参考
        """
        query = db.query(QA_Item).filter(
            QA_Item.status == QAStatus.published,
            QA_Item.is_deleted == False
        )
        
        published_qas = query.limit(100).all()  # 限制查询数量以提高性能
        
        similar_qas = []
        
        for qa in published_qas:
            similarity = cls.calculate_similarity(question, qa.question)
            if similarity >= 50:  # 只显示相似度 50% 以上的
                similar_qas.append({
                    "id": qa.id,
                    "question": qa.question,
                    "answer": qa.answer,
                    "similarity": similarity,
                    "category": f"{qa.main_category} - {qa.sub_category}"
                })
        
        # 按相似度排序并返回前 limit 个
        similar_qas.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_qas[:limit]
