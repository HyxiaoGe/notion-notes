# Langchain

_Last updated: 2025-02-02 23:12:01_

---

不同LLM模型之间的输入输出结构存在差异，这些差异会导致开发者需要频繁修改代码，降低代码的可维护性。为了解决这个问题，Langchain应用框架应运而生。


## 为什么选择LangChain


LangChain作为一个强大的框架，具有以下优势：


- **组件化和标准化**：提供了标准化的接口来处理各种LLM，使开发更加灵活和可维护。

- **丰富的工具集成**：内置了大量工具和集成，可以轻松连接数据库、搜索引擎等外部服务。

- **链式处理能力**：可以将多个组件组合成链，实现复杂的处理流程。

- **内存管理**：提供了多种记忆组件，使应用能够保持上下文连贯性。

## LangChain简介


LangChain是一个用于开发由语言模型驱动的应用程序的框架。它具有以下核心特点：


### 核心组件


- **Models (模型)**：负责与各种语言模型的交互接口，支持多种LLM、聊天模型和文本嵌入模型的统一调用

- **Prompts (提示)**：专门用于管理和优化提示模板，提供标准化的提示工程工具

- **Indexes (索引)**：提供高效的文档加载、分割和向量存储系统，支持大规模文本处理和检索

- **Memory (记忆)**：用于在交互过程中管理和存储状态信息，确保对话的连贯性和上下文理解

- **Chains (链)**：能将多个组件组合成端到端应用的核心机制，实现复杂的处理流程

- **Agents (代理)**：赋予LLM使用工具的能力，支持自主推理和行动决策

**Prompts组件介绍**


**概念与作用**


在LLM应用开发中,我们通常不会直接将用户输入传递给大模型,而是会将用户输入添加到一个更大的文本片段中,这个文本片段被称为Prompt。Prompt为大模型提供了任务相关的上下文和指令,帮助模型更好地理解和执行任务。


LangChain中的Prompts组件提供了一系列工具来管理和优化这些提示模板。主要包含两大类:


- PromptTemplate: 将Prompt按照template进行格式化,处理变量和组合

- Selectors: 根据不同条件选择不同的提示词

**基本构成**


在LangChain中,Prompts组件包含多个子组件:


角色提示模板:


提示模板类型:


**关键操作**


格式化LangChain支持两种格式化方式


提示模板拼接


**模板复用**


对于复杂的提示模板,LangChain提供了PipelinePromptTemplate来实现模板的复用:


最佳实践


**Model组件详解**


1. 基本概念
    Models是LangChain的核心组件，提供了一个标准接口来封装不同类型的LLM进行交互。LangChain本身不提供LLM,而是提供了接口来集成各种模型。
    LangChain支持两种类型的模型:
    - LLM: 使用纯文本作为输入和输出的大语言模型
    - Chat Model: 使用聊天消息列表作为输入并返回聊天消息的聊天模型

2. 组件架构
    LangChain中Models组件的基类结构如下:
    3. BaseLanguageModel(基类)
        - BaseLLM(大语言模型基类)
            - SimpleLLM(简化大语言模型)
            - 第三方LLM集成(OpenAI、百度文心等)
        - BaseChatModel(聊天模型基类)
            - SimpleChatModel(简化聊天模型)
            - 第三方Chat Model集成
    4. Message组件类型:
        - SystemMessage: 系统消息
        - HumanMessage: 人类消息
        - AIMessage: AI消息
        - FunctionMessage: 函数调用消息
        - ToolMessage: 工具调用消息

1. 最佳实践
    2. 选择合适的模型类型
        3. 简单文本生成任务使用LLM
        4. 对话类任务使用Chat Model
    5. 正确处理异步操作
        6. 在异步环境中使用ainvoke/astream
        7. 批量处理时考虑使用batch
    8. 异常处理
        9. 处理模型调用可能的超时
        10. 捕获API错误并适当处理
    11. 性能优化
        12. 合理使用批处理
        13. 适时使用流式输出

**OutputParser 解析器组件**


3. Parser类型详解
    Langchain 提供了多种Parser：
    4. 基础Parser：
        - StrOutputParser: 最简单的Parser,原样返回文本
        - BaseOutputParser: 所有Parser的基类
        - BaseLLMOutputParser: 专门用于LLM输出的基类
    5. 格式化Parser：
        - JsonOutputParser: 解析JSON格式输出
        - XMLOutputParser: 解析XML格式输出
        - PydanticOutputParser: 使用Pydantic模型解析输出
    6. 列表类Parser：
        - CommaSeparatedListOutputParser: 解析逗号分隔的列表
        - NumberedListOutputParser: 解析数字编号的列表

1. 最佳实践
    2. 选择合适的Parser
        - 简单文本使用StrOutputParser
        - 结构化数据使用JsonOutputParser或PydanticOutputParser
        - 列表数据使用专门的列表Parser
    3. 提示设计
        - 在提示中明确指定输出格式
        - 使用Parser提供的format_instructions
    4. 异常处理
        - 总是处理可能的解析错误
        - 考虑添加重试机制
        - 提供合理的默认值
    5. 性能优化
        - 避免过于复杂的解析逻辑
        - 合理使用缓存

**LCEL表达式与Runnable协议**


1. **Runnable协议核心方法**
    - invoke/ainvoke: 调用组件
    - batch/abatch: 批量处理
    - stream/astream: 流式输出
    - transform: 转换输入输出

1. 最佳实践
    2. 链的设计
        - 使用管道操作符(|)构建简单链
        - 复杂逻辑使用RunnableParallel
        - 数据传递用RunnablePassthrough
    3. 错误处理
        - 合理使用try/except
        - 实现错误回调处理
    4. 性能优化
        - 合适场景使用并行执行
        - 批处理代替单个处理
    5. 代码可维护性
        - 链结构保持清晰
        - 适当拆分复杂链
