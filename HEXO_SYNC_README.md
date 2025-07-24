# Notion to Hexo 同步工具

这个工具可以将你的Notion内容自动同步到Hexo博客。

## 功能特点

- 🔄 自动将Notion页面转换为Hexo文章格式
- 📝 自动生成Front Matter（标题、日期、标签、分类）
- 🖼️ 自动下载并保存图片到Hexo仓库
- 🏷️ 智能标签提取（根据标题内容）
- 📂 保持Notion的页面层级结构
- ⚡ 增量更新（只同步有变化的内容）
- 🚀 GitHub Actions自动化部署

## 使用方法

### 1. 配置环境变量

在GitHub仓库的Settings -> Secrets中添加以下secrets：

- `NOTION_TOKEN`: Notion API Token
- `ACTIONS_TOKEN`: GitHub Personal Access Token（需要repo权限）
- `NOTION_PAGE_ID`: 要同步的Notion根页面ID

### 2. 手动运行

```bash
# 设置环境变量
export NOTION_TOKEN="your-notion-token"
export GITHUB_TOKEN="your-github-token"
export NOTION_PAGE_ID="your-notion-page-id"
export HEXO_REPO="HyxiaoGe/blog"

# 运行同步
python notion_to_hexo.py
```

### 3. 自动运行

GitHub Actions会：
- 每天北京时间早上8点自动运行
- 可以在Actions页面手动触发

## 工作流程

1. **获取Notion内容** → 从指定页面递归获取所有内容
2. **转换格式** → 将Notion blocks转换为Markdown，生成Hexo Front Matter
3. **处理图片** → 下载Notion中的图片并保存到Hexo仓库
4. **更新仓库** → 将转换后的文章推送到Hexo源码仓库
5. **构建部署** → 自动运行hexo generate并部署到GitHub Pages

## 文件组织

```
blog/
├── source/
│   ├── _posts/              # 文章存放位置
│   │   ├── 2025-01-23-文章标题.md
│   │   └── ...
│   └── medias/
│       └── featureimages/
│           └── blog/        # 图片存放位置
│               └── 文章标题/
│                   └── image.png
```

## Front Matter格式

```yaml
---
title: 文章标题
date: 2025-01-23 10:30:00
categories: 分类名称
tags:
  - 标签1
  - 标签2
---
```

## 注意事项

1. 所有Notion页面都会被同步为博客文章
2. 子页面会作为独立的文章发布
3. 删除的Notion页面不会自动从博客删除
4. 图片会被下载并存储在GitHub仓库中

## 配置文件示例

创建 `hexo_config.yaml`：

```yaml
notion_token: "your-notion-token"
github_token: "your-github-token" 
notion_page_id: "your-page-id"
hexo_repo: "HyxiaoGe/blog"
hexo_source_branch: "master"
hexo_posts_path: "source/_posts"
hexo_images_path: "source/medias/featureimages/blog"
```