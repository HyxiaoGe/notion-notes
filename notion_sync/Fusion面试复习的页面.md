# Fusion面试复习的页面

_Last updated: 2025-07-25 15:25:17_

---

# Fusion API 项目面试 Q&A


#  Q1: LLM适配器是怎么设计的？


LLM 适配器主要采用工厂模式 + 适配器模式的组合设计：


1. **工厂模式统一模型创建**
    - 每个 LLM 提供商都有独立的工厂类（AnthropicFactory、OpenAIFactory 等）
    - 都实现相同的 create_model() 接口
    - LLMManager 统一管理所有工厂，根据 provider 参数选择对应工厂

2. **适配器模式处理差异化功能**
    - FunctionCall，文件处理提供统一的函数调用接口，只需要通过统一的方法，就可以调用不同LLM来处理。
    - 比如 FunctionCall适配器，只需要通过模型提供商，模型名称，function name就可以调用内部对应的function，执行结果之后，就会返回统一的结果，比如Dict 字典。
    - 文件上传适配：文心一言需要 base64 格式，通义千问需要图片URL格式

# Q2: 流式响应的SSE技术实现是怎样的？前后端如何配合？


**SSE数据格式设计**：


完整的SSE事件数据结构包含四个字段：


- type: 事件类型（reasoning_start、content、done等）

- conversation_id: 会话ID

- content: 内容（可选）

- message_id: 消息ID（可选，用于前端精确更新UI）

**流式处理核心机制**：


- **占位符机制**：流开始前先在数据库创建空消息获取message_id，流结束后更新完整内容

- **异步生成器**：使用AsyncGenerator实时yield数据，通过FastAPI的StreamingResponse返回

- **累积机制**：边流式输出边累积完整响应，保证数据库最终一致性

**三种流式处理策略**：


- **普通流**：一个message_id，直接输出内容

- **推理流**：两个message_id，分别处理思考过程（reasoning_message.id）和最终答案（assistant_message.id）

- **函数调用流**：检测函数调用、执行函数、继续对话的复杂流程

**事件类型体系**：


- **推理相关**：reasoning_start/content/complete

- **函数调用**：function_call_detected/function_result

- **搜索相关**：generating_query/performing_search/synthesizing_answer

- **基础事件**：content/done/error

**前后端协作机制**：


- 前端通过EventSource连接SSE端点

- 根据type判断事件类型，根据message_id更新对应UI组件

- 收到[DONE]信号后关闭连接

- 支持断网重连和错误处理

**技术优势**：实时性好、支持长文本不超时、数据一致性保证、可扩展多种流式策略


# Q3: Function Calling框架是如何实现的？“检测-执行-合成”三阶段流程具体是什么？


**三阶段流程详解**：


1.** 检测阶段（Detection）**


- LLM分析用户问题，判断是否需要调用外部工具（联网搜索、实践课程八旬、文件分析）

- 如用户问“今天的新闻”，LLM检测到需要调用hot_topics函数

- 检测到后发送function_call_detected事件通知前端

**2. 执行阶段（Execution）**


- **联网搜索**：调用WebSearchService，支持互联网实时信息获取

- **数据库查询**：调用DatabaseService，获取预先设置的sql模板，执行对应的查询方法，并填充sql参数

- **文件分析：**分析用户上传文件，支持摘要、数据提取、问答

- 执行过程通过SSE实时反馈状态（如“正在搜索...”）

**3. 合成阶段（Synthesis）**


- 函数执行结果不直接返回用户

- 将结果作为新上下文，让LLM进行二次处理

- LLM综合多源数据，生成更准确、更有价值的回答

框架实现特点：


**1. 函数注册机制**


- 通过FunctionRegistry统一管理所有可调用函数

- 每个函数包含：名称、描述、参数定义、处理器、分类标签

**2. 适配器统一接口**


- FunctionCallAdapter处理不同LLM的函数调用格式差异

- 支持OpenAI、Anthropic、DeepSeek等多种格式

**3. 流式处理集成**


- 函数调用完全融入流式响应

- 用户实时看到：“检测到需要搜索”→“正在搜索”→“正在生成答案”

- 每个阶段都有对应的事件类型和UI反馈

**4. 多工具组合**


- 一次对话可调用多个工具

- 工具之间可以协同工作

已实现的工具集成：


- web_search: 互联网搜索，获取实时信息

- hot_topics: 热点话题，涮盖科技、财经等领域

- analyze_file: 文件分析，支持摘要、数据提取、问答

**核心价值**：让AI不再局限于静态知识，而是能够获取实时信息、处理用户数据、追踪热点事件，实现“从用户问题到多源数据整合的智能化处理”


# Q4: Function Calling中的适配器具体是如何处理不同LLM格式差异的？


适配器处理的两个方向：


1. 输出格式适配（发送给LLM时）


**通用函数定义（一次性注册）**：


- name: 函数名

- description: 函数描述（告诉LLM这个函数干什么用的）

- parameters: JSON Schema结构（告诉LLM参数格式）

**适配器转换成不同格式**：


- OpenAI/DeepSeek格式: {"type": "function", "function": {...}}

- Anthropic格式: {"name": "...", "description": "...", "input_schema": {...}}

2. 输入格式适配（解析LLM响应时）


LLM返回的完整结构（包含其他字段）：


OpenAI格式：


- role: "assistant", content: null/文本

- tool_calls: [{"id": "call_abc123", "type": "function", "function": {"name": "web_search", "arguments": "{...}"}}]

Anthropic格式：


- role: "assistant", content: "描述文本"

- additional_kwargs.tool_calls: [{"id": "toolu_xyz789", "function": {"name": "web_search", "arguments": "{...}"}}]

适配器的复杂工作：


- 从不同的嵌套结构中准确提取函数调用信息

- 保留调用ID（call_abc123/toolu_xyz789）用于后续关联

- 最终提取出统一格式：{"name": "web_search", "arguments": "{...}"}

关键理解：


- LLM不执行函数，只是返回“函数调用指令”

- 给LLM的是“函数定义模板”，LLM返回的是“实例化调用”

- 后端适配器解析调用指令，找到对应handler真正执行

# Q5: Function Calling与Agent的概念区别


本质区别：响应式 vs 主动式


- **Function Calling（项目实现）**：响应式工具调用，用户问题→LLM检测→选择工具→执行→综合结果，单轮次线性流程

- **Agent智能代理**：主动式任务执行，制定多步骤计划→动态调整策略→组合工具使用→有状态记忆和反思能力

**角色定位差异**：


- Function Calling: LLM是"调度员" - 识别需求→选择工具→处理结果

- Agent: LLM是"执行者" - 制定策略→执行计划→监控进度→优化方案

**实现复杂度对比**：


- Function Calling: 预定义工具集，三阶段固定流程，无状态
