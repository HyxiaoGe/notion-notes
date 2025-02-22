# 大模型 RAG 应用开发基础及入门

_Last updated: 2025-02-22 08:21:39_

---

# 大语言模型中的幻觉问题(上)


# 什么是大语言模型的幻觉？


大语言模型在处理自然语言时，有时候会出现”幻觉“现象。所谓幻觉，就是模型生成的内容与事实或上下文不一致的问题。这些问题会严重影响AI应用的可靠性和实用性。


# 幻觉的两大类型


# 事实性幻觉


指模型生成的内容与实际事实不匹配。比如在回答"第一个登上月球的人是谁?"这个问题时:


- 错误回答: "Charles Lindbergh在1951年月球任务中第一个登上月球"

- 正确事实: Neil Armstrong才是第一个登上月球的人(1969年阿波罗11号任务)

这种幻觉之所以危险，是因为模型生成的内容看起来很可信，但实际上完全错误。


# 忠实性幻觉


指模型生成的内容与提供的上下文不一致。这种幻觉可以分为三类：


- 输出与原文不一致（编出原文中没有的信息）

- 上下文之间不一致（前后矛盾）

- 逻辑链不一致（推理过程存在漏洞）

比如在总结新闻时，模型可能会添加原文中不存在的细节，或者前后描述矛盾。


# 为什么会产生幻觉？


大语言模型产生幻觉的原因主要来自三个方面：


1. 数据源导致的幻觉
    - 训练数据中的质量问题
    - 数据中存在的错误信息
    - 数据覆盖范围有限

2. 训练过程导致的幻觉
    - 架构限制：无法准确理解长文本的上下文关联
    - 累积错误：生成过程中的错误会逐步传递和放大

3. 推理相关的幻觉
    - 回答过于简略
    - 生成过程中的不完整推理

# 如何评估幻觉问题


为了客观评估模型的幻觉问题，我们可以使用多种方法：


1. 事实一致性评估：将生成内容与权威来源进行比对

2. 分类器评估：使用专门训练的模型来检测是否存在幻觉

3. 问答测量：通过问答来验证生成内容的一致性

4. 不确定度分析：评估模型对自身输出的确信程度

5. 提示测量：让模型自我评估，通过特定提示策略来评估生成内容

# 大语言模型中的幻觉问题(下)：


# RAG解决方案


# RAG是什么？


**RAG**（Retrieval-Augmented Generation）也叫**检索增强生成**，是指对大语言模型输出进行优化，使其能够参考并利用数据源之外的权威知识。简单来说，RAG就是从外部检索对应的知识内容，和用户的提问一起构成Prompt发给大模型，再让大模型生成内容。


它的核心思想是：


1. **从外部知识库检索相关信息**

2. **将检索到的信息作为上下文提供给模型**

3. **让模型基于这些上下文生成回答**

简单来说：RAG = 外部知识检索 + Prompt构建 + LLM 生成


![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/4d514fab-2492-4877-a269-a017b8992bb6/c4c615d5-19f1-4c9d-8caa-eee0f593fefc/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4666FNJNWLW%2F20250222%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250222T002124Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQDde9tE2Hb8Z%2FdrWQTm1JoES%2FelnbfNI1VJqX3whK5CZQIgH72HwGcK%2FxHZ8u9ub031h8RreGDWgr8u%2BfV5XitI1H8qiAQI4f%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDMOxT2FABYcAaZ1e7CrcAx6oSbtDHrqQG6KJWM9DX82Px5eguRoXB8w4FVl1q%2BvnlN5BsXc1FAPBi99cB4KtyWnSobEVdO0e%2BdjHjWpnevpPOZjq9oShZ9X45ksNFN4ix5nz2CgF4RkeaBBNR78rZ%2FMDEmdFST3uMv1IK4BmG0DCpA4nUJTKJAIvf1tPEuUiyBaPo4c1qzlmo0IrJQdVpWITtGXu9P2X9BcT3qVPL%2FQuFsvQROQVY90jLHOWAxpBPbbISr%2B4CIkDdb6rqRVVNQ%2BG51dRozgsNpzIaCU6Mad2M1ljBA83uov%2BmoibqyAJDf1l2PcWeCrHTGPb2fKwMlg6%2FmyEsQ7NalN8CgLz664ZlBK7rAhVkKD50FQcfoS2ugBR1zsWla0MsY2iPLvTj%2FbaB2EdJFJDhjAolB3kzmNZHV0EyKx19FIVDuk5fFzhj2XFR8lzTl8VPAsK%2BtI4Jl8vnCmuTsGH8%2FDDcYjuRpoLdXcQKeEjS3yARuO8c8iHNqPKOKF%2BtX357uc6OgaFDvCP2741tteCilJGSUiyH1q9VPCxA7Pte8kNpqCbZOwL8edDPihZcLTMqqa6ZDaJ%2BXO7Jx%2BdcOVYBLhajpWLPn20XgKveGXVE79hQA%2FS2OUHor979hPlJvaYMw%2FRMOiu5L0GOqUB4vugdLFicCBvJCDgB43JbfCQLbXOZliNKveMyIVDxGtLGRNlB50wYjorjtt4TVGShhpY4%2BB9LWh013avs2SgpdX498t%2BCqjtI63uwS8Z%2BbbmH8M%2FsMTPFZXrasxkRkag8XUTZePQnfZh5AQ736wKdN83jxkqy2QSuBFefuBKG2Rf3y3ZpJ54HFdgO74oMeMAOeft1JGOt9fx8S2L4GKAvCqAxwmL&X-Amz-Signature=441b5b043cdccf5c712268aadb472f7243fa5d2ade6beaea8fff5fc1ac0ea1c9&X-Amz-SignedHeaders=host&x-id=GetObject)


# 为什么需要RAG？


LLM虽然是一个强大的工具，但它本身拒绝了解任何时事，且它给出的答案总是非常流畅，内容却不一定靠谱。这存在几个主要的问题:


1. LLM的训练数据量有限且无法更新到最新知识。

2. 当用户需要专业或领域特定的数据时，LLM往往缺乏相应的知识

3. 对于答案的问答内容很难从源创进行溯源

4. 由于技术限制，不同的训练源使用相同的大语言技术，可能会产生不确信的响应

而RAG为解决这些问题带来了以下优势：


- **经济高效**：预训练和微调模型的成本很高，而RAG是一种经济高效的新方法

- **信息时效**：使用RAG可以为LLM提供最新的研究、统计数据或新闻

- **增强用户信任度**：RAG允许LLM通过来源归属来呈现具体的信息，输出可以包括对来源的引文或参考，这可以增加对对话的生成式人工智能解决方案的任何信心

# RAG是如何工作的？


RAG采用三种主要的检索方式：


1. **一次性检索**：
    - 从单次检索中获取相关知识
    - 直接预置到大模型的提示词中
    - 不会收集反馈信息

2. **迭代检索**：
    - 允许在对话过程中多次检索
    - 每一轮都可能有新的检索
    - 支持多轮对话优化

3. **事后检索**：
    - 先生成答案
    - 然后检索验证
    - 对答案进行修正

![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/4d514fab-2492-4877-a269-a017b8992bb6/4686426d-2314-4f87-ba63-abeb1a60669f/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4666FNJNWLW%2F20250222%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250222T002124Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQDde9tE2Hb8Z%2FdrWQTm1JoES%2FelnbfNI1VJqX3whK5CZQIgH72HwGcK%2FxHZ8u9ub031h8RreGDWgr8u%2BfV5XitI1H8qiAQI4f%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDMOxT2FABYcAaZ1e7CrcAx6oSbtDHrqQG6KJWM9DX82Px5eguRoXB8w4FVl1q%2BvnlN5BsXc1FAPBi99cB4KtyWnSobEVdO0e%2BdjHjWpnevpPOZjq9oShZ9X45ksNFN4ix5nz2CgF4RkeaBBNR78rZ%2FMDEmdFST3uMv1IK4BmG0DCpA4nUJTKJAIvf1tPEuUiyBaPo4c1qzlmo0IrJQdVpWITtGXu9P2X9BcT3qVPL%2FQuFsvQROQVY90jLHOWAxpBPbbISr%2B4CIkDdb6rqRVVNQ%2BG51dRozgsNpzIaCU6Mad2M1ljBA83uov%2BmoibqyAJDf1l2PcWeCrHTGPb2fKwMlg6%2FmyEsQ7NalN8CgLz664ZlBK7rAhVkKD50FQcfoS2ugBR1zsWla0MsY2iPLvTj%2FbaB2EdJFJDhjAolB3kzmNZHV0EyKx19FIVDuk5fFzhj2XFR8lzTl8VPAsK%2BtI4Jl8vnCmuTsGH8%2FDDcYjuRpoLdXcQKeEjS3yARuO8c8iHNqPKOKF%2BtX357uc6OgaFDvCP2741tteCilJGSUiyH1q9VPCxA7Pte8kNpqCbZOwL8edDPihZcLTMqqa6ZDaJ%2BXO7Jx%2BdcOVYBLhajpWLPn20XgKveGXVE79hQA%2FS2OUHor979hPlJvaYMw%2FRMOiu5L0GOqUB4vugdLFicCBvJCDgB43JbfCQLbXOZliNKveMyIVDxGtLGRNlB50wYjorjtt4TVGShhpY4%2BB9LWh013avs2SgpdX498t%2BCqjtI63uwS8Z%2BbbmH8M%2FsMTPFZXrasxkRkag8XUTZePQnfZh5AQ736wKdN83jxkqy2QSuBFefuBKG2Rf3y3ZpJ54HFdgO74oMeMAOeft1JGOt9fx8S2L4GKAvCqAxwmL&X-Amz-Signature=0cc1745ec909f56e5d4f5dd16e1649780ee1f620e08adb0cff93635456d777c2&X-Amz-SignedHeaders=host&x-id=GetObject)


# RAG实战示例


以一个简单的问答场景为例，展示RAG的实际应用流程:


1. 用户提问:"公司有销售什么产品？"

2. 系统处理流程:
    - 使用检索器获取产品相关文档
    - 将文档内容与问题组合成提示词
    - 通过LLM生成回答
    - 确保回答基于检索到的事实信息

3. 最终输出:包含准确的产品信息，并且所有信息都可以溯源。

# AI应用开发利器：向量数据库详解


# 什么是向量数据库？


向量数据库（Vector Database）是一种专门用于存储和处理向量数据的数据库系统。它不同于传统的关系型数据库，因为它需要将所有数据映射为特定的向量格式，并采用相似性搜索作为主要的检索方式。


# 一个生动的例子：识别猫咪


让我们通过一个识别猫咪的例子来理解向量数据库。假设我们有一组不同品种的猫咪图片：


- 波斯猫

- 英国短毛猫

- 暹罗猫

- 布偶猫

- 无毛猫

每张猫咪图片都可以用一组数字向量来表示其特征，如:


```javascript
波斯猫: [0.4, 0.3, 0.4, 0.5, 0.3, 0.4, 0.5, ...]
英国短毛猫: [0.7, 0.2, 0.5, 0.5, 0.5, 0.5, 0.5, ...]
暹罗猫: [0.5, 0.3, 0.4, 0.5, 0.3, 0.4, 0.5, ...]
```


这些数字代表了猫咪的各种特征，比如:


- 毛发长度

- 体型大小

- 面部特征

- 耳朵形状等等

# 向量数据库的优势


与传统的数据库相比，向量数据库有以下特点：


1. **数据类型**：
    - 传统数据库：数值、字符串、时间等结构化数据
    - 向量数据库：向量数据(不存储原始数据，有的也支持)

2. **数据规模**：
    - 传统数据库：小，1亿条数据对关系型数据库来说规模很大
    - 向量数据库：大，最少千亿数据是基线

3. **数据组织方式**：
    - 传统数据库：基于表格、按照行和列组织
    - 向量数据库：基于向量、按向量维度组织

4. **查找方式**：
    - 传统数据库：精确查找/范围查找
    - 向量数据库：近似查找，查询结果是与输入向量最相似的向量

# 相似性搜索算法


在向量数据库中，支持通过多种方式来计算两个向量的相似度：


**余弦相似度**：主要是用于衡量向量在方向上的相似性，特别适用于文本、图像和高维空间中的向量。它不受向量长度的影响，只考虑方向的相似程度，计算公式如下（计算两个向量间的夹角的余弦值，取值范围为[-1, 1]）：


```shell
similarity(A,B) = (A·B)/(||A||·||B||)
```


**欧式距离**：主要是用于衡量向量之间的直线距离，得到的值可能很大，最小为0，通常用于低维空间或需要考虑向量各个维度之间差异的情况。欧式距离较小的向量被认为更相似，计算公式如下：


```shell
distance(A,B) = √∑(Ai-Bi)²
```


例如下图：左侧就是`欧式距离`，右侧就是`余弦相似度`。


![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/4d514fab-2492-4877-a269-a017b8992bb6/5ffcc1e2-d42e-43e1-8304-359cfa6e287b/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB4666FNJNWLW%2F20250222%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250222T002124Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjELj%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQDde9tE2Hb8Z%2FdrWQTm1JoES%2FelnbfNI1VJqX3whK5CZQIgH72HwGcK%2FxHZ8u9ub031h8RreGDWgr8u%2BfV5XitI1H8qiAQI4f%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2Mzc0MjMxODM4MDUiDMOxT2FABYcAaZ1e7CrcAx6oSbtDHrqQG6KJWM9DX82Px5eguRoXB8w4FVl1q%2BvnlN5BsXc1FAPBi99cB4KtyWnSobEVdO0e%2BdjHjWpnevpPOZjq9oShZ9X45ksNFN4ix5nz2CgF4RkeaBBNR78rZ%2FMDEmdFST3uMv1IK4BmG0DCpA4nUJTKJAIvf1tPEuUiyBaPo4c1qzlmo0IrJQdVpWITtGXu9P2X9BcT3qVPL%2FQuFsvQROQVY90jLHOWAxpBPbbISr%2B4CIkDdb6rqRVVNQ%2BG51dRozgsNpzIaCU6Mad2M1ljBA83uov%2BmoibqyAJDf1l2PcWeCrHTGPb2fKwMlg6%2FmyEsQ7NalN8CgLz664ZlBK7rAhVkKD50FQcfoS2ugBR1zsWla0MsY2iPLvTj%2FbaB2EdJFJDhjAolB3kzmNZHV0EyKx19FIVDuk5fFzhj2XFR8lzTl8VPAsK%2BtI4Jl8vnCmuTsGH8%2FDDcYjuRpoLdXcQKeEjS3yARuO8c8iHNqPKOKF%2BtX357uc6OgaFDvCP2741tteCilJGSUiyH1q9VPCxA7Pte8kNpqCbZOwL8edDPihZcLTMqqa6ZDaJ%2BXO7Jx%2BdcOVYBLhajpWLPn20XgKveGXVE79hQA%2FS2OUHor979hPlJvaYMw%2FRMOiu5L0GOqUB4vugdLFicCBvJCDgB43JbfCQLbXOZliNKveMyIVDxGtLGRNlB50wYjorjtt4TVGShhpY4%2BB9LWh013avs2SgpdX498t%2BCqjtI63uwS8Z%2BbbmH8M%2FsMTPFZXrasxkRkag8XUTZePQnfZh5AQ736wKdN83jxkqy2QSuBFefuBKG2Rf3y3ZpJ54HFdgO74oMeMAOeft1JGOt9fx8S2L4GKAvCqAxwmL&X-Amz-Signature=5831d87c3fb018017ea0e49611d9288c51556cc052a80eff67044152a1a4e1be&X-Amz-SignedHeaders=host&x-id=GetObject)


# 实际应用场景


向量数据库的主要应用场景包括：


1. 人脸识别

2. 图像搜索

3. 音频识别

4. 智能推荐系统

这些场景的共同特点是：需要对非结构化数据（如图片、文本、音频）进行相似度搜索。


在RAG中，我们会将文档的知识按特定规则分成小块，转换成向量存储到向量数据库中。当人类提问时，我们将问题转换为向量，在数据库中找到最相似的文本块，这些文本块可以成为Prompt的补充内容。


# 深入理解Embedding嵌入技术


# Embedding 是什么？


Embedding(嵌入)是一种在机器学习中广泛使用的技术，它能将文本、图片、视频等非结构化数据映射到向量空间中。一个Embedding向量通常是一个包含N个浮点数的数组，这个向量不仅表示了数据的特征，更重要的是通过学习可以表达它们的内在语义。简而言之，Embedding就是一个模型生成方法，可以将非结构化的数据，例如文本/图片/视频等数据映射成有意义的向量数据。比如一段文本、一张图片、一段视频，警告Embedding模型处理后都会变成类似这样的向量：

