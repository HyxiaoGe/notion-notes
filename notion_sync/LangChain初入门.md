# LangChain初入门

_Last updated: 2025-02-08 08:15:01_

---

不同LLM模型之间的输入输出结构存在差异，这些差异会导致开发者需要频繁修改代码，降低代码的可维护性。为了解决这个问题，Langchain应用框架应运而生。


# 为什么选择LangChain


LangChain作为一个强大的框架，具有以下优势：


- **组件化和标准化**：提供了标准化的接口来处理各种LLM，使开发更加灵活和可维护。

- **丰富的工具集成**：内置了大量工具和集成，可以轻松连接数据库、搜索引擎等外部服务。

- **链式处理能力**：可以将多个组件组合成链，实现复杂的处理流程。

- **内存管理**：提供了多种记忆组件，使应用能够保持上下文连贯性。

# LangChain简介


LangChain是一个用于开发由语言模型驱动的应用程序的框架。


# 核心组件


- **Models (模型)**：提供与大语言模型的统一交互接口，支持各类LLM、聊天模型和文本嵌入模型的调用

- **Prompts (提示)**：专门用于管理和优化提示模板，提供标准化的提示工程工具

- **Indexes (索引)**：提供高效的文档加载、分割和向量存储系统，支持大规模文本处理和检索

- **Memory (记忆)**：用于在交互过程中管理和存储状态信息，确保对话的连贯性和上下文理解

- **Chains (链)**：能将多个组件组合成端到端应用的核心机制，实现复杂的处理流程

- **Agents (代理)**：赋予LLM使用工具的能力，支持自主推理和行动决策

![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/4d514fab-2492-4877-a269-a017b8992bb6/7c5c69d7-7584-4b18-93ac-72f0968bfd6b/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466VNE2EFGJ%2F20250208%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250208T001440Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEGgaCXVzLXdlc3QtMiJHMEUCID3FO1xRgjeVuSz74T7zcriS2B6i%2FLoffhrfkAuOUmLTAiEAxK0CCngR3in17zD5WUyl2UhX0it5qf0P8KXxzjxH044qiAQIgf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDHs6gPmXmEKF5KfbnircA4uz%2F1ICgGSG2gTNeet1wTa3dW%2FAlzUnkblVvi7%2B46N2a1jATXY1FVstnGcM6NnRzwRRbiluNy8A2ozwdU81TPMQy6TAa8LjNkMVNJO8eFRN8OSjqZSGDXVDfjqM4oiAEf5Y6KwrQtuqncz2syTYfp1my9pix7p4PBK92YrGnfGLvZig9DVVNK47GyCp%2B1yeu40lJQiz1ybkWZbKM%2F%2B6eXrJPYPoByivKbuuiL1Tryd0dxWiWQleNT%2FuK9g6vJ4mQU1zC0BRFYtQlFJqBFKsGHdCBr92HCAiBjw0R6%2FTE%2FK5lFkSjKaC0U70wdUzAHaPDdPJXd%2Fz3Wxpji8SjxnUpjf1%2FOUtvgwgE8IN809xlsmvLmQbTISnCazpSJwv9tfaVwqHRMdAUWWojIieCfQashpSTPgKEbw%2BeV8LrfVjQyNmZPtpPYxZfzUjzkuRlHCfbuFNGl5oSvXR3WlSYfIyW5%2FJAAoG8eDy4PbwIzDvtctlguzPWOJKQtBWdcrMA4c3MAUIq3lBfv4D6kcCQkw2sVmvft6gDmSv%2BSlcSfpmAdKuXqFx1XDN9oEQLljjZtvFi1sMr6hhVi9%2BAvQN1L%2BaqMsvgdDo5a7be91uEjli4WpLO3PsFchIlUWGDtPLMLu%2Bmr0GOqUBMN75Q%2FEkgHLCtGrwCqcrRc23JswKdvDwFEQi8AC%2BednrlfuGpQapA6XKv97jIwo1pXnkfOx0mWkHixA5tEDcLTL6EZ4nu4X9Nm1s6Gs2W0W8aJiHLyZayJxGxi6XfPoszTQFsS3fY7XxwKFy4mh5pQTl2I7kQrHrjLmWHWfQ%2FgHxO3h5PRHNa6%2FEBKemBNCBMGwKIvtv8Pw2px6jy4PcVfbU1LuS&X-Amz-Signature=04d4f3c02307d0778353b8aa4a5eb40c96cb10af1c76fbc902dd4ece999999f4&X-Amz-SignedHeaders=host&x-id=GetObject)


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

```python
# f-string方式
prompt = PromptTemplate.from_template("请将一个关于{subject}的笑话")

# jinja2方式
prompt = PromptTemplate.from_template(
    "请将一个关于{{subject}}的笑话",
    template_format="jinja2"
)
```


提示模板拼接

```python
# 字符串提示拼接
prompt = (
    PromptTemplate.from_template("请将一个关于{subject}的冷笑话")
    + "，让我开心下"
    + "\n使用{language}语言。"
)

# 聊天提示拼接
system_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是OpenAI开发的聊天机器人，请根据用户的提问进行回复，我叫{username}")
])
human_prompt = ChatPromptTemplate.from_messages([
    ("human", "{query}")
])
prompt = system_prompt + human_prompt
```


**模板复用**


对于复杂的提示模板,LangChain提供了PipelinePromptTemplate来实现模板的复用:

```python
# 描述提示模板
instruction_template = "你正在模拟{person}。"
instruction_prompt = PromptTemplate.from_template(instruction_template)

# 示例提示模板
example_template = """下面是一个交互例子:
Q: {example_q}
A: {example_a}"""
example_prompt = PromptTemplate.from_template(example_template)

# 开始提示模板
start_template = """现在开始对话:
Q: {input}
A:"""
start_prompt = PromptTemplate.from_template(start_template)

# 组合模板
pipeline_prompt = PipelinePromptTemplate(
    final_prompt=full_prompt,
    pipeline_prompts=[
        ("instruction", instruction_prompt),
        ("example", example_prompt),
        ("start", start_prompt),
    ]
)
```


**最佳实践**


选择合适的格式化方式


1. 简单变量替换使用f-string

2. 需要条件判断等复杂逻辑时使用jinja2

提示模板设计


1. 保持模板的清晰和可维护性

2. 合理使用系统消息和示例

3. 避免过于复杂的嵌套结构

错误处理


1. 验证必要的变量是否存在

2. 处理格式化可能出现的异常

性能优化


1. 重复使用的模板要缓存

2. 避免不必要的模板拼接操作

**Model组件详解**


**基本概念**

Models是LangChain的核心组件，提供了一个标准接口来封装不同类型的LLM进行交互，LangChain本身不提供LLM,而是提供了接口来集成各种模型。


LangChain支持两种类型的模型:


- LLM: 使用纯文本作为输入和输出的大语言模型

- Chat Model: 使用聊天消息列表作为输入并返回聊天消息的聊天模型



**组件架构**

LangChain中Models组件的基类结构如下:


BaseLanguageModel(基类)

- BaseLLM(大语言模型基类)
    - SimpleLLM(简化大语言模型)
    - 第三方LLM集成(OpenAI、百度文心等)

- BaseChatModel(聊天模型基类)
    - SimpleChatModel(简化聊天模型)
    - 第三方Chat Model集成



Message组件类型:

- SystemMessage: 系统消息

- HumanMessage: 人类消息

- AIMessage: AI消息

- FunctionMessage: 函数调用消息

- ToolMessage: 工具调用消息



**核心办法**

Models组件提供了几个关键方法:


invoke/invoke_sync: 调用模型生成内容

```python
# 基本调用
llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
response = llm.invoke("你好!")

# 异步调用
async def generate():
    response = await llm.ainvoke("你好!")
```


batch/abatch: 批量调用处理多个输入

```python
messages = [
    "请讲一个关于程序员的笑话",
    "请讲一个关于Python的笑话"
]
responses = llm.batch(messages)
```


stream/astream: 流式返回生成内容

```python
response = llm.stream("请介绍下LLM和LLMOps")
for chunk in response:
    print(chunk.content, end="")
```


**Message组件使用**

消息组件用于构建与聊天模型的交互:


```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 创建消息
system_msg = SystemMessage(content="你是一个AI助手")
human_msg = HumanMessage(content="你好!")
ai_msg = AIMessage(content="你好!我是AI助手")

# 构建消息列表
messages = [system_msg, human_msg, ai_msg]

# 使用消息与模型交互
response = chat_model.invoke(messages)
```


**实践示例**

基本对话示例：


```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 创建聊天模型
chat = ChatOpenAI()

# 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位{role}"),
    ("human", "{query}")
])

# 调用模型
response = chat.invoke(
    prompt.format_messages(
        role="Python专家",
        query="什么是装饰器?"
    )
)
```


流式输出示例：


```python
# 创建提示模板
prompt = ChatPromptTemplate.from_template("{subject}的发展历史是什么?")

# 创建模型
llm = ChatOpenAI()

# 流式生成
response = llm.stream(
    prompt.format_messages(subject="人工智能")
)

# 处理输出
for chunk in response:
    print(chunk.content, end="")
```


**最佳实践**


选择合适的模型类型


1. 简单文本生成任务使用LLM

2. 对话类任务使用Chat Model

正确处理异步操作


1. 在异步环境中使用ainvoke/astream

2. 批量处理时考虑使用batch

异常处理


1. 处理模型调用可能的超时

2. 捕获API错误并适当处理

性能优化


1. 合理使用批处理

2. 适时使用流式输出

**OutputParser 解析器组件**


为什么需要输出解析器

在使用大模型时,我们经常会遇到输出解析的问题。比如:


```python
llm = ChatOpenAI()

# 示例1: 返回的是自然语言
llm.invoke("1+1等于几?")  # 输出: 1 + 1 等于 2。

# 示例2: 包含多余信息
llm.invoke("告诉我3个动物的名字。")  # 输出: 好的，这里有三种动物的名字：\n1. 狮子\n2. 大熊猫\n3. 斑马

# 示例3: 格式不统一
llm.invoke("给我一个json数据,键为a和b")  # 输出: {\n "a": 10,\n "b": 20\n}
```


OutputParser就是为了解决这些问题而设计的。它通过:


1. 预设提示 - 告诉LLM需要的输出格式

2. 解析功能 - 将输出转换成指定格式



**Parser类型详解**

Langchain 提供了多种Parser：


1. 基础Parser：
    - StrOutputParser: 最简单的Parser,原样返回文本
    - BaseOutputParser: 所有Parser的基类
    - BaseLLMOutputParser: 专门用于LLM输出的基类

2. 格式化Parser：
    - JsonOutputParser: 解析JSON格式输出
    - XMLOutputParser: 解析XML格式输出
    - PydanticOutputParser: 使用Pydantic模型解析输出

3. 列表类Parser：
    - CommaSeparatedListOutputParser: 解析逗号分隔的列表
    - NumberedListOutputParser: 解析数字编号的列表



**实践示例**

1. StrOutputParser使用：
```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 创建链
chain = (
    ChatPromptTemplate.from_template("{query}")
    | ChatOpenAI()
    | StrOutputParser()
)

# 调用
response = chain.invoke({"query": "你好!"})
```


2. JsonOutputParser使用：
```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

# 定义输出结构
class Joke(BaseModel):
    joke: str = Field(description="回答用户的冷笑话")
    punchline: str = Field(description="冷笑话的笑点")

# 创建Parser
parser = JsonOutputParser(pydantic_object=Joke)

# 创建提示模板
prompt = ChatPromptTemplate.from_template(
    "回答用户的问题。\n{format_instructions}\n{query}\n"
)

# 添加格式说明
prompt = prompt.partial(format_instructions=parser.get_format_instructions())

# 创建链
chain = prompt | ChatOpenAI() | parser

# 使用
response = chain.invoke({"query": "请讲一个关于程序员的冷笑话"})
```


**错误处理**

1. 解析失败的处理：
```python
from langchain_core.output_parsers import OutputParserException

try:
    result = parser.parse(llm_output)
except OutputParserException as e:
    # 处理解析错误
    print(f"解析错误: {e}")
    # 可以选择重试或使用默认值
```


2. 使用重试机制：
```python
# 可以配置回调来处理重试
from langchain_core.callbacks import BaseCallbackHandler

class RetryHandler(BaseCallbackHandler):
    def on_retry(self, retry_state):
        print(f"重试次数: {retry_state.attempt_number}")
```


**最佳实践**

1. 选择合适的Parser
    - 简单文本使用StrOutputParser
    - 结构化数据使用JsonOutputParser或PydanticOutputParser
    - 列表数据使用专门的列表Parser

2. 提示设计
    - 在提示中明确指定输出格式
    - 使用Parser提供的format_instructions

3. 异常处理
    - 总是处理可能的解析错误
    - 考虑添加重试机制
    - 提供合理的默认值

4. 性能优化
    - 避免过于复杂的解析逻辑
    - 合理使用缓存



**LCEL表达式与Runnable协议**


**为什么需要LCEL**

传统的链式调用方式存在嵌套问题：


```python
content = parser.invoke(
    llm.invoke(
        prompt.invoke(
            {"query": req.query.data}
        )
    )
)
```


LCEL 提供了更优雅的方式：


```python
chain = prompt | llm | parser
content = chain.invoke({"query": req.query.data})
```


**Runnable协议核心方法**

- invoke/ainvoke: 调用组件

- batch/abatch: 批量处理

- stream/astream: 流式输出

- transform: 转换输入输出



**两个核心类**

1. RunnableParallel - 并行执行多个Runnable
```python
from langchain_core.runnables import RunnableParallel

# 并行执行多个链
chain = RunnableParallel(
    joke=joke_chain,
    poem=poem_chain
)
resp = chain.invoke({"subject": "程序员"})
```


2. RunnablePassthrough - 传递数据
```python
from langchain_core.runnables import RunnablePassthrough

# 构建检索链
chain = (
    RunnablePassthrough.assign(
        context=lambda query: retrieval(query)
    )
    | prompt 
    | llm 
    | parser
)
```


**实践示例**

1. 基础链构建：
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# 创建组件
prompt = ChatPromptTemplate.from_template("{input}")
llm = ChatOpenAI()
parser = StrOutputParser()

# 构建链
chain = prompt | llm | parser

# 执行
response = chain.invoke({"input": "Hello!"})
```


2. 带检索的链：
```python
def retrieval(query: str) -> str:
    return "相关文档内容..."

# 构建链
chain = (
    {
        "context": retrieval,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

# 执行
response = chain.invoke("问题")
```


**最佳实践**

1. 链的设计
    - 使用管道操作符(|)构建简单链
    - 复杂逻辑使用RunnableParallel
    - 数据传递用RunnablePassthrough

2. 错误处理
    - 合理使用try/except
    - 实现错误回调处理

3. 性能优化
    - 合适场景使用并行执行
    - 批处理代替单个处理

4. 代码可维护性
    - 链结构保持清晰
    - 适当拆分复杂链


