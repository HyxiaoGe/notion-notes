import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import requests
import yaml
from github import Github
from notion_client import Client as NotionClient
from retrying import retry


class HexoContentConvert:
    """Hexo格式内容转换器"""
    
    def __init__(self, hexo_config: dict):
        self.hexo_config = hexo_config
        self.list_states = []
        self.current_numbered_list = 0
        self.in_numbered_list = False
        self.numbered_list_counter = 0
        self.processed_pages = set()
        self.logger = logging.getLogger("HexoConvert")
        
    def convert_to_hexo_post(self, page_data: Dict, categories: List[str] = None) -> Tuple[str, str, List[Dict]]:
        """
        将Notion页面转换为Hexo文章格式
        返回: (文件名, 内容, 图片列表)
        """
        page = page_data['page']
        page_id = page['id']
        
        # 获取页面标题
        title = self._get_page_title(page)
        
        # 重置图片列表
        self.pending_images = []
        
        # 获取创建时间和更新时间
        created_time = page.get('created_time', datetime.now().isoformat())
        last_edited_time = page.get('last_edited_time', created_time)
        
        # 生成文件名 (使用创建日期和标题)
        date_str = datetime.fromisoformat(created_time.replace('Z', '+00:00')).strftime('%Y-%m-%d')
        safe_title = self._sanitize_filename(title)
        filename = f"{date_str}-{safe_title}.md"
        
        # 构建Front Matter
        front_matter = self._build_front_matter(title, created_time, categories)
        
        # 转换内容（传递标题用于图片处理）
        content = self._convert_page_content(page_data, include_title=False, page_title=title)
        
        # 组合最终内容
        full_content = f"{front_matter}\n{content}"
        
        return filename, full_content, self.pending_images
    
    def _build_front_matter(self, title: str, created_time: str, categories: List[str] = None) -> str:
        """构建Hexo的Front Matter"""
        # 格式化日期
        date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        
        front_matter = f"""---
title: {title}
date: {date_str}"""
        
        # 添加分类
        if categories and len(categories) > 0:
            front_matter += f"\ncategories: {categories[0]}"
        
        # 根据标题推测标签
        tags = self._extract_tags_from_title(title)
        if tags:
            front_matter += "\ntags:"
            for tag in tags:
                front_matter += f"\n  - {tag}"
        
        front_matter += "\n---"
        return front_matter
    
    def _extract_tags_from_title(self, title: str) -> List[str]:
        """从标题中提取可能的标签"""
        tags = []
        
        # 技术关键词映射
        tech_keywords = {
            'spring': ['Spring', 'Java'],
            'react': ['React', 'Frontend'],
            'vue': ['Vue', 'Frontend'],
            'docker': ['Docker', 'DevOps'],
            'kubernetes': ['Kubernetes', 'K8s', 'DevOps'],
            'python': ['Python'],
            'java': ['Java'],
            'javascript': ['JavaScript', 'JS'],
            'typescript': ['TypeScript', 'TS'],
            'golang': ['Go', 'Golang'],
            'rust': ['Rust'],
            'mysql': ['MySQL', 'Database'],
            'redis': ['Redis', 'Cache'],
            'kafka': ['Kafka', 'MessageQueue'],
            'rabbitmq': ['RabbitMQ', 'MessageQueue'],
            'elasticsearch': ['Elasticsearch', 'Search'],
            'mongodb': ['MongoDB', 'NoSQL'],
            'git': ['Git', 'Version Control'],
            'linux': ['Linux', 'OS'],
            'aws': ['AWS', 'Cloud'],
            'azure': ['Azure', 'Cloud'],
            'langchain': ['LangChain', 'AI'],
            'ai': ['AI', 'Artificial Intelligence'],
            'ml': ['Machine Learning', 'ML'],
            'rag': ['RAG', 'AI'],
            'llm': ['LLM', 'AI'],
        }
        
        # 转换为小写进行匹配
        title_lower = title.lower()
        
        for keyword, tag_list in tech_keywords.items():
            if keyword in title_lower:
                tags.extend(tag_list)
        
        # 去重
        return list(set(tags))
    
    def _get_page_title(self, page: Dict) -> str:
        """获取页面标题"""
        try:
            title_property = page['properties'].get('title', {}).get('title', [])
            if title_property and len(title_property) > 0:
                return title_property[0]['plain_text']
            return "Untitled"
        except (KeyError, IndexError):
            return "Untitled"
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        # 替换不合法的文件名字符
        filename = re.sub(r'[<>:"/\\|?*]', '-', filename)
        # 替换空格为连字符
        filename = filename.replace(' ', '-')
        # 移除多余的连字符
        filename = re.sub(r'-+', '-', filename)
        # 移除首尾的连字符
        filename = filename.strip('-')
        return filename[:100]  # 限制长度
    
    def _convert_page_content(self, page_data: Dict, include_title: bool = True, page_title: str = None) -> str:
        """转换页面内容为Markdown"""
        # 重置计数器
        self.numbered_list_counter = 0
        
        markdown_lines = []
        
        if include_title:
            page = page_data['page']
            title = self._get_page_title(page)
            markdown_lines.append(f"# {title}\n")
        
        # 处理blocks
        if 'blocks' in page_data:
            blocks = page_data['blocks']
            if isinstance(blocks, dict) and 'results' in blocks:
                blocks = blocks['results']
            
            for block in blocks:
                # 跳过子页面块（这些会被单独处理）
                if block['type'] == 'child_page':
                    continue
                    
                block_content = self._convert_block(block, page_title=page_title)
                if block_content:
                    markdown_lines.append(block_content)
        
        return '\n'.join(filter(None, markdown_lines))
    
    def _convert_block(self, block: Dict, page_title: str = None) -> str:
        """转换单个块为Markdown"""
        try:
            block_type = block['type']
            block_data = block.get(block_type, {})
            
            # 处理各种块类型
            if block_type == 'paragraph':
                text = self._convert_rich_text(block_data.get('rich_text', []))
                return f"{text}\n" if text else ''
                
            elif block_type == 'heading_1':
                text = self._convert_rich_text(block_data.get('rich_text', []))
                return f"## {text}\n" if text else ''
                
            elif block_type == 'heading_2':
                text = self._convert_rich_text(block_data.get('rich_text', []))
                return f"### {text}\n" if text else ''
                
            elif block_type == 'heading_3':
                text = self._convert_rich_text(block_data.get('rich_text', []))
                return f"#### {text}\n" if text else ''
                
            elif block_type == 'bulleted_list_item':
                indent = "  " * len(self.list_states)
                text = self._convert_rich_text(block_data.get('rich_text', []))
                result = f"{indent}- {text}\n"
                
                if block.get('has_children') and 'children' in block:
                    self.list_states.append('bulleted')
                    for child in block['children']['results']:
                        child_content = self._convert_block(child, page_title)
                        if child_content:
                            result += child_content
                    if self.list_states:  # 检查列表是否为空
                        self.list_states.pop()
                
                return result
                
            elif block_type == 'numbered_list_item':
                if not self.in_numbered_list:
                    self.current_numbered_list = 0
                    self.list_states = []
                
                self.in_numbered_list = True
                self.current_numbered_list += 1
                indent = "  " * len(self.list_states)
                text = self._convert_rich_text(block_data.get('rich_text', []))
                result = f"{indent}{self.current_numbered_list}. {text}\n"
                
                if block.get('has_children') and 'children' in block:
                    self.list_states.append('numbered')
                    for child in block['children']['results']:
                        child_content = self._convert_block(child, page_title)
                        if child_content:
                            result += child_content
                    if self.list_states:  # 检查列表是否为空
                        self.list_states.pop()
                
                return result
                
            elif block_type == 'code':
                text = self._convert_rich_text(block_data.get('rich_text', []))
                language = block_data.get('language', '')
                return f"```{language}\n{text}\n```\n" if text else ''
                
            elif block_type == 'quote':
                text = self._convert_rich_text(block_data.get('rich_text', []))
                return f"> {text}\n" if text else ''
                
            elif block_type == 'image':
                return self._handle_image(block_data, page_title)
                
            elif block_type == 'table':
                table_data = block.get('table', {})
                children = block.get('children', {}).get('results', [])
                return self._handle_table(table_data, block['id'], children)
            
            # 重置列表状态
            if block_type not in ['bulleted_list_item', 'numbered_list_item']:
                self.in_numbered_list = False
                self.list_states = []
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error converting block: {str(e)}")
            return ""
    
    def _convert_rich_text(self, rich_text: List[Dict]) -> str:
        """转换富文本"""
        if not rich_text:
            return ""
        
        text_parts = []
        for text in rich_text:
            content = text.get('plain_text', '')
            annotations = text.get('annotations', {})
            
            # 处理文本格式
            if annotations.get('bold'):
                content = f"**{content}**"
            if annotations.get('italic'):
                content = f"*{content}*"
            if annotations.get('strikethrough'):
                content = f"~~{content}~~"
            if annotations.get('code'):
                content = f"`{content}`"
            
            # 处理链接
            if text.get('href'):
                content = f"[{content}]({text['href']})"
            
            text_parts.append(content)
        
        return ''.join(text_parts)
    
    def _handle_image(self, image_data: Dict, page_title: str = None) -> str:
        """处理图片"""
        try:
            url = image_data['file']['url']
            caption = ""
            if image_data.get('caption'):
                caption = self._convert_rich_text(image_data['caption'])
            
            alt_text = caption if caption else "image"
            
            # 保存图片URL和标题，供后续下载使用
            if not hasattr(self, 'pending_images'):
                self.pending_images = []
            
            self.pending_images.append({
                'url': url,
                'page_title': page_title or 'untitled',
                'alt_text': alt_text
            })
            
            # 返回占位符，后续会替换为实际路径
            return f"![{alt_text}]({url})\n"
            
        except Exception as e:
            self.logger.error(f"Error handling image: {str(e)}")
            return ""
    
    def _handle_table(self, table_data: Dict, block_id: str, children: List[Dict]) -> str:
        """处理表格"""
        if not children:
            return ""
        
        rows = []
        header_row = None
        
        for row in children:
            if row['type'] != 'table_row':
                continue
            
            cells = []
            for cell in row['table_row']['cells']:
                cell_text = self._convert_rich_text(cell)
                cell_text = cell_text.replace('|', '\\|') if cell_text else ''
                cells.append(cell_text.strip())
            
            if not header_row:
                header_row = cells
            else:
                rows.append(cells)
        
        if not header_row:
            return ""
        
        # 构建Markdown表格
        table = []
        table.append('| ' + ' | '.join(header_row) + ' |')
        table.append('| ' + ' | '.join(['---'] * len(header_row)) + ' |')
        
        for row in rows:
            while len(row) < len(header_row):
                row.append('')
            table.append('| ' + ' | '.join(row) + ' |')
        
        return '\n'.join(table) + '\n'


class NotionToHexoSync:
    """Notion到Hexo博客同步工具"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        
        # 初始化客户端
        self.notion = NotionClient(auth=self.config['notion_token'])
        self.github = Github(self.config['github_token'])
        
        # 初始化转换器
        self.converter = HexoContentConvert(self.config.get('hexo', {}))
        
        # 同步状态
        self.sync_status_file = "hexo_sync_status.json"
        self.last_sync_times = self._load_sync_status()
        
        self.logger.info("NotionToHexoSync initialized")
    
    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置"""
        config = {}
        
        # 环境变量映射
        env_mappings = {
            "NOTION_TOKEN": "notion_token",
            "GITHUB_TOKEN": "github_token",
            "NOTION_PAGE_ID": "notion_page_id",
            "HEXO_REPO": "hexo_repo",
            "HEXO_SOURCE_BRANCH": "hexo_source_branch",
            "BLOG_REPO": "blog_repo"
        }
        
        # 从环境变量读取
        for env_key, config_key in env_mappings.items():
            value = os.getenv(env_key)
            if value:
                config[config_key] = value
        
        # 从配置文件读取
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        for key, value in file_config.items():
                            if key not in config or not config[key]:
                                config[key] = value
            except Exception as e:
                raise ValueError(f"Failed to load config file: {str(e)}")
        
        # 设置默认值
        config.setdefault('hexo_source_branch', 'master')
        config.setdefault('hexo_posts_path', 'source/_posts')
        config.setdefault('hexo_images_path', 'source/medias/featureimages/blog')
        
        # 验证必需配置
        required_keys = ["notion_token", "github_token", "notion_page_id", "hexo_repo"]
        missing_keys = [key for key in required_keys if not config.get(key)]
        if missing_keys:
            raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")
        
        return config
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('hexo_sync.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("NotionToHexoSync")
    
    def _load_sync_status(self) -> dict:
        """加载同步状态"""
        try:
            if os.path.exists(self.sync_status_file):
                with open(self.sync_status_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading sync status: {str(e)}")
            return {}
    
    def _save_sync_status(self):
        """保存同步状态"""
        try:
            with open(self.sync_status_file, 'w') as f:
                json.dump(self.last_sync_times, f)
        except Exception as e:
            self.logger.error(f"Error saving sync status: {str(e)}")
    
    def _needs_update(self, page_id: str, last_edited_time: str) -> bool:
        """检查是否需要更新"""
        if page_id not in self.last_sync_times:
            return True
        
        try:
            last_sync = datetime.fromisoformat(self.last_sync_times[page_id].replace('Z', '+00:00'))
            current_edit = datetime.fromisoformat(last_edited_time.replace('Z', '+00:00'))
            return current_edit > last_sync
        except Exception as e:
            self.logger.error(f"Error comparing timestamps: {str(e)}")
            return True
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def _get_notion_content(self) -> Dict:
        """获取Notion内容"""
        try:
            self.logger.info(f"Fetching content from Notion page {self.config['notion_page_id']}")
            
            # 获取根页面
            root_page = self.notion.pages.retrieve(self.config['notion_page_id'])
            
            # 获取所有内容
            content = {
                'page': root_page,
                'blocks': self._get_all_blocks(self.config['notion_page_id'])
            }
            
            return content
        except Exception as e:
            self.logger.error(f"Error getting Notion content: {str(e)}")
            raise
    
    def _get_all_blocks(self, block_id: str) -> List[Dict]:
        """递归获取所有块"""
        blocks = []
        try:
            response = self.notion.blocks.children.list(block_id)
            blocks = response['results']
            
            for block in blocks:
                if block.get('has_children', False):
                    child_id = block['id']
                    child_blocks = self._get_all_blocks(child_id)
                    block['children'] = {
                        'results': child_blocks
                    }
                    
                    if block['type'] == 'child_page':
                        child_page = self.notion.pages.retrieve(child_id)
                        block['page_info'] = child_page
            
            return blocks
            
        except Exception as e:
            self.logger.error(f"Error getting blocks for {block_id}: {str(e)}")
            return blocks
    
    def _process_pages_recursively(self, page_data: Dict, categories: List[str] = None) -> List[Tuple[str, str, str, str, List[Dict]]]:
        """
        递归处理页面
        返回: [(文件名, 内容, page_id, last_edited_time, 图片列表), ...]
        """
        results = []
        
        try:
            page = page_data['page']
            page_id = page['id']
            last_edited_time = page.get('last_edited_time')
            
            # 获取标题作为分类
            title = self.converter._get_page_title(page)
            current_categories = categories.copy() if categories else []
            
            # 转换当前页面
            filename, content, images = self.converter.convert_to_hexo_post(page_data, current_categories)
            results.append((filename, content, page_id, last_edited_time, images))
            
            # 将当前页面标题添加到分类路径
            current_categories.append(title)
            
            # 处理子页面
            if 'blocks' in page_data:
                blocks = page_data['blocks']
                for block in blocks:
                    if block['type'] == 'child_page':
                        child_page_data = {
                            'page': block['page_info'],
                            'blocks': block.get('children', {}).get('results', [])
                        }
                        child_results = self._process_pages_recursively(child_page_data, current_categories)
                        results.extend(child_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing page: {str(e)}")
            return results
    
    def _update_hexo_repo(self, filename: str, content: str, page_id: str, last_edited_time: str, images: List[Dict]):
        """更新Hexo仓库"""
        if not self._needs_update(page_id, last_edited_time):
            self.logger.info(f"Content not changed for {filename}, skipping update")
            return
        
        try:
            repo = self.github.get_repo(self.config['hexo_repo'])
            
            # 先处理图片
            if images:
                for img in images:
                    new_url = self._download_and_save_image(img['url'], img['page_title'])
                    # 替换内容中的图片URL
                    content = content.replace(img['url'], new_url)
            
            # 构建文件路径
            file_path = f"{self.config['hexo_posts_path']}/{filename}"
            
            # 标准化路径
            file_path = file_path.replace(os.sep, '/')
            
            # 更新或创建文件
            try:
                file = repo.get_contents(file_path, ref=self.config['hexo_source_branch'])
                repo.update_file(
                    file_path,
                    f"Update from Notion: {filename}",
                    content,
                    file.sha,
                    branch=self.config['hexo_source_branch']
                )
                self.logger.info(f"Updated file {file_path}")
            except:
                repo.create_file(
                    file_path,
                    f"Create from Notion: {filename}",
                    content,
                    branch=self.config['hexo_source_branch']
                )
                self.logger.info(f"Created file {file_path}")
            
            # 更新同步状态
            self.last_sync_times[page_id] = last_edited_time
            self._save_sync_status()
            
        except Exception as e:
            self.logger.error(f"Error updating Hexo repo: {str(e)}")
            raise
    
    def _download_and_save_image(self, url: str, page_title: str) -> str:
        """下载图片并保存到Hexo仓库"""
        try:
            # 下载图片
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            ext = url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                ext = 'png'
            
            safe_title = self.converter._sanitize_filename(page_title)
            image_filename = f"{safe_title}_{timestamp}.{ext}"
            
            # 构建路径
            image_path = f"{self.config['hexo_images_path']}/{safe_title}/{image_filename}"
            image_path = image_path.replace(os.sep, '/')
            
            # 检查文件是否已存在
            repo = self.github.get_repo(self.config['hexo_repo'])
            try:
                repo.get_contents(image_path, ref=self.config['hexo_source_branch'])
                self.logger.info(f"Image already exists: {image_path}")
            except:
                # 文件不存在，创建新文件
                repo.create_file(
                    image_path,
                    f"Add image: {image_filename}",
                    response.content,
                    branch=self.config['hexo_source_branch']
                )
                self.logger.info(f"Saved image: {image_path}")
            
            # 返回相对路径
            return f"/medias/featureimages/blog/{safe_title}/{image_filename}"
            
        except Exception as e:
            self.logger.error(f"Error downloading image: {str(e)}")
            return url  # 失败时返回原URL
    
    def sync(self):
        """执行同步"""
        try:
            # 获取Notion内容
            notion_content = self._get_notion_content()
            if not notion_content:
                self.logger.warning("No content fetched from Notion")
                return
            
            # 处理所有页面
            pages = self._process_pages_recursively(notion_content)
            
            # 更新到Hexo仓库
            for filename, content, page_id, last_edited_time, images in pages:
                self._update_hexo_repo(filename, content, page_id, last_edited_time, images)
            
            self.logger.info("Sync completed successfully")
            
        except Exception as e:
            self.logger.error(f"Sync failed: {str(e)}")
            raise


def main():
    parser = argparse.ArgumentParser(description='Notion to Hexo sync tool')
    parser.add_argument('--config', type=str, help='Path to config file')
    args = parser.parse_args()
    
    try:
        syncer = NotionToHexoSync(config_path=args.config)
        syncer.sync()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()