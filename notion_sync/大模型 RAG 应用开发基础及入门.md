# 大模型 RAG 应用开发基础及入门

_Last updated: 2025-02-05 14:05:30_

---

# 大语言模型中的幻觉问题(上)


## 什么是大语言模型的幻觉？


大语言模型在处理自然语言时


## 为什么需要RAG？


大语言模型虽然强大，但经常会产生“幻觉”，即生成看似合理但实际不准确的内容。这种幻觉主要有两类：


1. **事实性幻觉** - 生成的内容与事实不符

2. **忠实性幻觉** - 生成的内容与上下文不一致

为了解决这个问题，我们需要让模型基于可靠的知识来源生成内容，这就是RAG技术的由来。


## RAG是什么？


**RAG**（Retrieval-Augmented Generation）是一种将外部知识库与大语言模型相结合的技术。它的核心思想是：


1. **从外部知识库检索相关信息**

2. **将检索到的信息作为上下文提供给模型**

3. **让模型基于这些上下文生成回答**

简单来说：RAG = 外部知识检索 + Prompt构建 + LLM 生成


![image](https://prod-files-secure.s3.us-west-2.amazonaws.com/4d514fab-2492-4877-a269-a017b8992bb6/c4c615d5-19f1-4c9d-8caa-eee0f593fefc/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466QCMN4HCG%2F20250205%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250205T060529Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjECYaCXVzLXdlc3QtMiJIMEYCIQDOKeAf%2FggBS6qz0CdVg7glQBkbw28%2FxiZSJm24sw%2BrLAIhALqdgTBoUuS1iY8gjm1q3gSq4GlKuZdXwffZjSiRiHKRKv8DCD8QABoMNjM3NDIzMTgzODA1IgzQT2NJFCH4wPgnEb0q3ANqdsii%2Bo9URxVkaAmW9%2BqmX4pAtOegs9vKOgmAADP4lrcPEIcxyvgRIg8XWhTh8FOw%2B91E0G2KDVlkGkGAN3DNatMVDHRk6I%2F2HAIPbKFhq4q2NLHUoz6GCoqFKEc2b0LhFGoKVVSGX1s8NjCPvmOXuWaQGTO16x4RZv2%2BelgttOc8uiJp8P%2B0qaMA60k4k76YNhmAx8v1wjpqUenC%2F8ylBPk2FZfxLwMxsY51FvPSdzDCLvX6bfeOZAQnfSZPea%2BJD2glUMJkK5eki9dnZ70AqZdvUBwlvhd7q8B%2F12Kri3hdLs%2FKE9ggSCxY3lR%2Ffl%2FyNy7Kflq1t%2F34ue1HdpCdrU9p0X9IKjuEWo0yjQpUmVTtxU%2BRDZcIbt1XbUNtSfDovoMin7%2FuwmaOA8YEADVh1z3j91GUuzPiNy1VIFiqjZT%2FhWlwjBBX7%2BitZVdezw9E4MU32H6EVOiNqC7zfCYAstF5reYhhRyZSUTZUgizOUoDiRgeZiHas%2B%2BvaXd2e4vDOPpRlx9ylXdrRwEqjZPIluhPW6DJcsnThoVQNpxojpUufm2QqEchT6fZJknQTEj1REcNe90uwM3aE3aYshcMvev4468O%2Fy1qalw%2BZ%2FPYg4M13vJ9tdcmMFRadjDV%2BYu9BjqkASezZk88hISqjpmQ0%2BVOIGoS4uxMyGpvlowKtyGWF366j8YC1VurUnpV520oRCThOYfg1uKYrSCXk6noeqAsGEia2zME0LmptDUCeXV4fmtxIiJdrxbdYEwKE4pQKOU%2FxLQnZXfl7nLMZiV%2BjNlFgFv8bdBRKAULyXbOLn2E3HgZ9eeM2hmB2iS3jBv0TtSIfRAo1OKH%2FRkhmWGasLNHv5ozeldv&X-Amz-Signature=973a9c921437eae32341fb6f4c00624a09c8f2a4702ae75511c4b03683d0dd9a&X-Amz-SignedHeaders=host&x-id=GetObject)


## 向量数据库：RAG的核心组件


要实现高效的知识检索，我们需要使用向量数据库。它与传统数据库的主要区别是：


- **存储方式**：基于向量而不是表格

- **检索方式**：基于相似度计算而不是精确匹配

- **应用场景**：更适合非结构化数据的语义检索

## 嵌入（Embedding）技术


Embedding 是实现知识检索的关键技术，它可以：


1. 将文本、图片等非结构化数据转换成向量

2. 使用余弦相似度等算法计算向量间的相似度

3. 帮助实现语义层面的相似性搜索

现代嵌入模型（如OpenAI的text-embedding-ada-002）可以生成高质量的语义向量，为RAG应用提供了坚实的基础。

