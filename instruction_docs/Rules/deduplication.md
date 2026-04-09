# 查重规则

## 查重算法

### 算法选择
- 库：`fuzzywuzzy`
- 备选：`rapidfuzz`（推荐生产环境使用）

### 相似度计算
```python
from fuzzywuzzy import fuzz

def calculate_similarity(text1: str, text2: str) -> float:
    """计算两个文本的相似度"""
    # 转换为小写
    t1 = text1.lower().strip()
    t2 = text2.lower().strip()

    # 使用模糊匹配
    ratio = fuzz.ratio(t1, t2)
    partial_ratio = fuzz.partial_ratio(t1, t2)

    # 综合评分（可调整权重）
    score = (ratio * 0.6 + partial_ratio * 0.4) / 100

    return score
```

## 查重阈值

### 阈值定义
| 阈值类型 | 值 | 说明 |
|----------|------|------|
| 高风险 | ≥ 95% | 几乎相同，直接提示合并 |
| 中风险 | ≥ 85% | 高度相似，需要人工确认 |
| 低风险 | ≥ 70% | 部分相似，可忽略 |

### 阈值配置
```python
# 可配置阈值
DUPLICATE_THRESHOLD = 0.85  # 85%

# 高风险阈值
HIGH_RISK_THRESHOLD = 0.95
```

## 查重流程

### 单条查重
```
1. 获取新 Q&A 内容
2. 与知识库所有内容比对
3. 计算相似度得分
4. 超过阈值 → 返回重复列表
5. 未超过阈值 → 允许创建
```

### 批量查重
```
1. 批量导入 Q&A
2. 两两比对（时间复杂度 O(n²)）
3. 生成重复矩阵
4. 返回所有重复对
5. 用户确认处理方式
```

## 查重结果展示

### 结果格式
```json
{
  "has_duplicates": true,
  "duplicates": [
    {
      "new_index": 0,
      "existing_id": 123,
      "similarity": 0.92,
      "new_question": "轮胎保修多久？",
      "existing_question": "轮胎保修多长时间？",
      "risk_level": "high"
    }
  ]
}
```

### 风险等级
- `high`: ≥ 95%，建议合并
- `medium`: 85%-95%，建议审核
- `low`: < 85%，可忽略

## 合并策略

### 自动合并条件
- 相似度 ≥ 95%
- 答案内容高度一致
- 用户确认合并

### 合并操作
```python
def merge_qa(new_qa: QA_Item, existing_qa: QA_Item):
    """合并两条相似的 Q&A"""
    # 保留更完整的答案
    if len(new_qa.answer) > len(existing_qa.answer):
        final_answer = new_qa.answer
    else:
        final_answer = existing_qa.answer

    # 记录合并历史
    merged_record = {
        "original_ids": [new_qa.id, existing_qa.id],
        "merged_at": datetime.now(),
        "final_answer": final_answer
    }

    return merged_record
```

## 性能优化

### 大数据量优化
- 当 Q&A 数量 > 10000 时，使用倒排索引
- 预计算常见词的相似度
- 增量查重（新 Q&A vs 最近修改的 Q&A）

### 异步查重
```python
# 后台任务执行查重
@router.post("/check_duplicates")
async def check_duplicates_background(
    background_tasks: BackgroundTasks,
    qa_content: str
):
    # 立即返回
    task_id = str(uuid.uuid4())

    # 后台执行查重
    background_tasks.add_task(run_duplicate_check, task_id, qa_content)

    return {"task_id": task_id, "status": "processing"}
```
