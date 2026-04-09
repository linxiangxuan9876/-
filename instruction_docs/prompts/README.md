# 优质 Prompt 集合

> 本目录收录了在 4S 店售后知识库项目中验证有效的 Prompt 模板

---

## 📋 目录索引

- [系统级 Prompts](./system-prompts.md) - 系统角色设定
- [分类 Prompts](./classification-prompts.md) - AI 分类相关
- [业务 Prompts](./business-prompts.md) - 业务场景应用

---

## 🎯 Prompt 设计原则

### 1. 结构清晰
```
角色设定 → 任务描述 → 输入格式 → 输出格式 → 约束条件
```

### 2. 变量明确
```
{variable} - 用户输入变量
[可选] - 可选参数
{default} - 默认值
```

### 3. 示例引导
```
好的 Prompt 应包含：
- 输入示例
- 期望输出示例
- 边界情况说明
```

### 4. 温度控制
| 场景 | Temperature | 说明 |
|------|-------------|------|
| 分类 | 0.0 - 0.3 | 确定性强 |
| 生成 | 0.7 - 0.9 | 创造性高 |
| 问答 | 0.3 - 0.5 | 平衡模式 |

---

## 🔧 通用工具函数

### Python 调用示例
```python
def call_gpt(prompt: str, temperature: float = 0.3) -> str:
    """通用 GPT 调用"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content

def parse_json_response(response: str) -> dict:
    """解析 JSON 响应"""
    import json
    import re

    # 提取 JSON 块
    match = re.search(r'\{[\s\S]*\}', response)
    if match:
        return json.loads(match.group())
    return {}
```

---

## 📝 Prompt 版本记录

| 版本 | 日期 | 变更内容 | 效果 |
|------|------|----------|------|
| v1.0 | 2026-04-08 | 初始版本 | 分类准确率 ~90% |
