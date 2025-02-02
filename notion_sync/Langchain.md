# Langchain

_Last updated: 2025-02-03 02:04:42_

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


- **Models (模型)**：提供与大语言模型的统一交互接口，支持各类LLM、聊天模型和文本嵌入模型的调用

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


- SystemMessagePromptTemplate: 系统角色消息模板

- HumanMessagePromptTemplate: 人类角色消息模板

- AIMessagePromptTemplate: AI角色消息模板

提示模板类型:


- PromptTemplate: 文本提示模板

- ChatPromptTemplate: 聊天消息提示模板

- MessagePlaceholder: 消息占位符

**关键操作**


格式化LangChain支持两种格式化方式


提示模板拼接


**模板复用**


对于复杂的提示模板,LangChain提供了PipelinePromptTemplate来实现模板的复用:


**最佳实践**


选择合适的格式化方式


1. 简单变量替换使用f-string

1. 需要条件判断等复杂逻辑时使用jinja2

提示模板设计


1. 保持模板的清晰和可维护性

1. 合理使用系统消息和示例

1. 避免过于复杂的嵌套结构

错误处理


1. 验证必要的变量是否存在

1. 处理格式化可能出现的异常

性能优化


1. 重复使用的模板要缓存

1. 避免不必要的模板拼接操作

**Model组件详解**


**OutputParser 解析器组件**


**LCEL表达式与Runnable协议**


1. **Runnable协议核心方法**
    - invoke/ainvoke: 调用组件
    - batch/abatch: 批量处理
    - stream/astream: 流式输出
    - transform: 转换输入输出
