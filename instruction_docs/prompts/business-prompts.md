# 业务 Prompts

> 用于特定业务场景的 Prompt 模板

---

## 1. 保修政策问答

### 保修期查询
```markdown
作为 4S 店服务顾问，请回答以下关于保修政策的问题：

问题：{user_question}

请根据以下保修政策信息回答：
{policy_content}

【回答要求】
1. 准确引用保修政策条款
2. 如涉及期限，说明具体时间或里程
3. 如有例外情况，主动说明
4. 回答简洁明了，不超过 200 字

如果问题超出保修政策范围，请回复："该问题需要进一步咨询，请致电客服热线。"
```

### 保修范围判断
```markdown
## 任务
判断以下情况是否在保修范围内。

## 情况描述
车型：{car_model}
购买日期：{purchase_date}
故障描述：{fault_description}
行驶里程：{mileage} 公里

## 保修政策要点
- 整车保修：3年或10万公里，以先到者为准
- 核心部件：发动机、变速箱 5年或15万公里
- 易耗部件不在保修范围内（如雨刮片、刹车片等）

## 输出格式
返回 JSON：
{
  "is_covered": true/false,
  "warranty_type": "整车保修/核心部件/易耗品/不在保修范围",
  "reason": "判断理由",
  "next_step": "建议的下一步操作"
}
```

---

## 2. 保养维护问答

### 保养周期咨询
```markdown
## 任务
根据车型提供保养周期建议。

## 车辆信息
车型：{car_model}
当前里程：{current_mileage} 公里
上次保养时间：{last_service_date}
上次保养里程：{last_service_mileage} 公里

## 标准保养周期
- 小保养（机油、机滤）：每 6 个月或 5000-10000 公里
- 大保养：每 12 个月或 20000 公里
- 轮胎换位：每 10000 公里
- 刹车片检查：每 20000 公里

## 输出要求
1. 判断是否需要立即保养
2. 给出下次建议保养时间/里程
3. 列出推荐保养项目
4. 估计保养费用范围

返回格式：
{
  "need_service": true/false,
  "urgency": "immediate/soon/can_wait",
  "recommended_items": ["保养项目1", "保养项目2"],
  "next_service_mileage": "XX公里或XX个月",
  "estimated_cost": "XX元"
}
```

---

## 3. 故障诊断问答

### 故障初步判断
```markdown
## 任务
根据用户描述的故障现象，提供初步诊断建议。

## 故障信息
车型：{car_model}
行驶里程：{mileage} 公里
故障现象：{symptom_description}
故障发生时间：{when_it_started}
故障频率：{frequency}

## 【重要】
你只能提供初步判断和建议，不能替代专业诊断。

## 输出格式
返回 JSON：
{
  "possible_causes": ["可能原因1", "可能原因2"],
  "severity": "low/medium/high/critical",
  "can_drive": true/false,
  "immediate_action": "紧急情况下的应对措施",
  "recommended_action": "建议的处理方式",
  "estimated_repair_cost": "预估费用范围"
}

【严重程度定义】
- low：可正常行驶，但建议尽快检查
- medium：建议 24 小时内到店检查
- high：建议立即到店检修
- critical：停止驾驶，联系救援
```

### 警告灯识别
```markdown
## 任务
识别并解释汽车警告灯的含义。

## 警告灯信息
车型：{car_model}
警告灯图标描述：{icon_description}
当前状态：{engine_status}/{temperature}/{speed}

## 常见警告灯定义
| 图标 | 含义 | 紧急程度 |
|------|------|----------|
| 发动机故障灯 | 发动机系统异常 | medium-high |
| 机油压力灯 | 机油不足或压力异常 | critical |
| 水温灯 | 发动机过热 | critical |
| 刹车警示灯 | 刹车系统异常 | critical |
| 电池灯 | 充电系统异常 | medium |

## 输出格式
{
  "likely_cause": "最可能的故障原因",
  "urgency_level": "critical/high/medium/low",
  "can_continue_driving": true/false,
  "immediate_steps": ["步骤1", "步骤2"],
  "recommended_action": "建议处理方式"
}
```

---

## 4. 配件更换问答

### 配件寿命咨询
```markdown
## 任务
提供配件更换周期建议。

## 配件信息
配件名称：{part_name}
车型：{car_model}
当前里程：{current_mileage} 公里
配件更换历史：{replacement_history}

## 标准配件寿命
| 配件 | 更换周期 |
|------|----------|
| 机油 | 5000-10000 公里 |
| 机滤 | 同机油 |
| 空滤 | 20000 公里 |
| 空调滤 | 20000 公里 |
| 刹车片 | 30000-50000 公里 |
| 刹车盘 | 换两次刹车片后 |
| 轮胎 | 5年或80000公里 |
| 火花塞 | 40000 公里 |
| 电池 | 3-5年 |
| 变速箱油 | 60000 公里 |

## 输出格式
{
  "is_replacement_needed": true/false,
  "remaining_life": "约XX公里或XX个月",
  "replacement_urgency": "immediate/soon/can_wait",
  "estimated_cost": "费用范围",
  "notes": "注意事项"
}
```

---

## 5. 服务预约问答

### 预约确认
```markdown
## 任务
生成服务预约确认信息。

## 预约信息
客户姓名：{customer_name}
联系电话：{phone}
车牌号：{license_plate}
车型：{car_model}
预约门店：{store_name}
预约时间：{appointment_datetime}
服务项目：{service_items}
备注：{notes}

## 输出格式
```json
{
  "confirmation_number": "预约编号",
  "appointment_details": {
    "store": "门店名称",
    "address": "门店地址",
    "time": "预约时间",
    "services": ["服务项目列表"]
  },
  "customer_info": {
    "name": "客户姓名",
    "phone": "联系电话",
    "vehicle": "车牌号 车型"
  },
  "preparation_notes": ["到店前准备事项"],
  "cancellation_policy": "取消/改期政策"
}
```
