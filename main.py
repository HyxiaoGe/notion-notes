import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

import yaml
from github import Github
from notion_client import Client as NotionClient
from retrying import retry


class Config:
    """配置管理类"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str = None) -> Dict:
        config = {}

        # 1. 首先尝试从环境变量读取
        env_mappings = {
            "NOTION_TOKEN": "notion_token",
            "GH_TOKEN": "github_token",
            "GITHUB_TOKEN": "github_token",
            "NOTION_PAGE_ID": "notion_page_id",
            "GITHUB_REPO": "github_repo"
        }

        for env_key, config_key in env_mappings.items():
            value = os.getenv(env_key)
            if value:
                config[config_key] = value

        # 2. 如果提供了配置文件，则读取
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding='utf-8') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        # 用文件配置补充未在环境变量中设置的项
                        for key, value in file_config.items():
                            if key not in config or not config[key]:  # 如果环境变量值为空也使用配置文件
                                config[key] = value
            except Exception as e:
                raise ValueError(f"Failed to load config file: {str(e)}")

        # 3. 设置默认值
        config.setdefault('sync_interval', 30)
        config.setdefault('base_path', 'notion_sync')

        # 4. 验证必要的配置项
        required_keys = ["notion_token", "github_token", "notion_page_id"]
        missing_keys = [key for key in required_keys if not config.get(key)]
        if missing_keys:
            raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")

        return config

    @property
    def notion_token(self) -> str:
        return self.config["notion_token"]

    @property
    def github_token(self) -> str:
        return self.config["github_token"]

    @property
    def notion_page_id(self) -> str:
        return self.config['notion_page_id']

    @property
    def github_repo(self) -> str:
        return self.config['github_repo']

    @property
    def sync_interval(self) -> int:
        return self.config.get('sync_interval', 30)

    @property
    def base_path(self) -> str:
        return self.config.get('base_path', 'notion_sync')


class ContentConvert:
    """内容格式转换器"""

    def __init__(self):
        # 用于跟踪列表的缩进级别
        self.list_states = []  # 用栈来跟踪列表状态
        self.current_numbered_list = 0  # 当前有序列表的计数
        self.in_numbered_list = False  # 是否在有序列表中
        self.list_indent_level = 0
        self.numbered_list_counter = 0  # 添加序号计数器
        self.table_data = {}  # 用于缓存表格数据
        self.processed_pages = set()  # 用于追踪已处理的页面
        self.page_map = {}  # 保存页面ID到文件路径的映射

    def convert_workspace(self, root_page: Dict, base_path: str) -> List[Tuple[str, str]]:
        """转换整个工作区"""
        self.processed_pages.clear()
        self.page_map.clear()

        # 创建根目录
        os.makedirs(base_path, exist_ok=True)

        # 获取根页面信息
        page = root_page["page"]
        title = page['properties']['title']['title'][0]['plain_text']

        return self._process_page_recursively(root_page, base_path, [])

    def _process_page_recursively(self, page_data: Dict, base_path: str, path_components: List[str]) -> List[
        Tuple[str, str]]:
        """递归处理页面及其子页面"""
        try:
            page = page_data['page']
            page_id = page['id']

            if page_id in self.processed_pages:
                return []

            self.processed_pages.add(page_id)

            # 获取标题并处理文件名
            title = page['properties']['title']['title'][0]['plain_text']
            file_name = self._sanitize_filename(title) + '.md'

            # 构建相对路径
            current_path = os.path.join(base_path, *path_components)

            # 创建目录（仅当不存在时）
            os.makedirs(current_path, exist_ok=True)

            # 构建文件完整路径
            file_path = os.path.join(current_path, file_name)

            # 转换内容
            content = self._convert_page_content(page_data)
            results = [(file_path, content)]

            # 处理子页面
            if 'blocks' in page_data:
                blocks = page_data['blocks']
                for block in blocks:
                    if block['type'] == 'child_page':
                        child_page = {
                            'page': block['page_info'],
                            'blocks': block.get('children', {}).get('results', [])
                        }
                        child_results = self._process_page_recursively(
                            child_page,
                            base_path,
                            path_components + [os.path.dirname(file_name)]
                        )
                        results.extend(child_results)

            return results
        except Exception as e:
            print(f"Error processing page: {str(e)}")
            return []

    def _generate_file_name(self, page_data: Dict) -> str:
        """生成文件名

        包含时间戳以避免冲突
        """
        title = self._get_page_title(page_data)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        return f"{self._sanitize_filename(title)}-{timestamp}.md"

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除不合法字符"""
        # 替换不合法的文件名字符
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '-')
        return filename.strip()

    def _convert_page_content(self, page_data: Dict) -> str:
        # 重置计数器
        self.numbered_list_counter = 0
        """转换页面内容为 Markdown 格式"""
        try:
            # 从page获取标题
            page = page_data['page']
            title = page['properties']['title']['title'][0]['plain_text']

            markdown_lines = [
                f"# {title}",
                f"\n_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n",
                "---\n"
            ]

            # 处理blocks
            if 'blocks' in page_data:
                blocks = page_data['blocks']
                if isinstance(blocks, dict) and 'results' in blocks:
                    blocks = blocks['results']

                for block in blocks:
                    block_content = self._convert_block(block)
                    if block_content:
                        markdown_lines.append(block_content)

            return '\n'.join(filter(None, markdown_lines))

        except Exception as e:
            return ""

    def _convert_block(self, block: Dict) -> str:
        """转换单个块为 Markdown"""
        try:
            block_type = block['type']
            block_data = block[block_type]

            if block_type == 'bulleted_list_item':
                # 处理基本列表项
                indent = "    " * len(self.list_states)  # 使用4个空格作为基本缩进
                text = self._convert_rich_text(block_data['rich_text'])
                result = f"{indent}- {text}\n"

                if block.get('has_children') and 'children' in block:
                    self.list_states.append('bulleted')
                    for child in block['children']['results']:
                        child_content = self._convert_block(child)
                        if child_content:
                            result += child_content
                    self.list_states.pop()

                return result
            elif block_type == 'numbered_list_item':
                if not self.in_numbered_list:
                    self.current_numbered_list = 0
                    self.list_states = []

                self.in_numbered_list = True
                self.current_numbered_list += 1
                indent = "    " * len(self.list_states)
                text = self._convert_rich_text(block_data['rich_text'])
                result = f"{indent}{self.current_numbered_list}. {text}\n"

                # 处理子项
                if block.get('has_children') and 'children' in block:
                    self.list_states.append('numbered')
                    for child in block['children']['results']:
                        # 增加了对paragraph类型的处理
                        if child['type'] == 'paragraph':
                            # 段落文本要缩进,但不加序号
                            child_text = self._convert_rich_text(child['paragraph']['rich_text'])
                            if child_text:
                                result += f"{indent}    {child_text}\n"
                        else:
                            child_content = self._convert_block(child)
                            if child_content:
                                result += child_content
                    self.list_states.pop()

                return result
            elif block_type == 'code':
                result = ''
                # 处理代码块
                text = self._convert_rich_text(block_data['rich_text'])
                language = block_data.get('language', '')
                if text:
                    result = f"```{language}\n{text}\n```\n\n"
                    return result

            # 不是列表项,清除列表状态
            self.in_numbered_list = False
            self.list_states = []

            if block_type == 'paragraph':
                # 先处理段落本身
                text = self._convert_rich_text(block_data.get('rich_text', []))
                result = f"{text}\n\n" if text else ''

                if block.get('has_children') and 'children' in block:
                    for child in block['children']['results']:
                        child_content = self._convert_block(child)
                        if child_content:
                            result += child_content

                return result
            elif block_type == 'heading_1':
                # 处理一级标题
                if 'rich_text' in block_data:
                    text = self._convert_rich_text(block_data['rich_text'])
                    return f"# {text}\n\n"

            elif block_type == 'heading_2':
                # 处理二级标题
                if 'rich_text' in block_data:
                    text = self._convert_rich_text(block_data['rich_text'])
                    return f"## {text}\n\n"

            elif block_type == 'heading_3':
                # 处理三级标题
                if 'rich_text' in block_data:
                    text = self._convert_rich_text(block_data['rich_text'])
                    return f"### {text}\n\n"

            elif block_type == 'code':
                # 处理代码块
                text = self._convert_rich_text(block_data['rich_text'])
                language = block_data.get('language', '')
                if text:
                    result = f"```{language}\n{text}\n```\n\n"
                    return result

            elif block_type == 'quote':
                # 处理引用
                text = self._convert_rich_text(block_data['rich_text'])
                return f"> {text}\n\n"

            return ""

        except Exception as e:
            return ""

    def _convert_paragraph(self, paragraph: Dict) -> str:
        """转换段落内容"""
        text = self._convert_rich_text(paragraph.get('rich_text', []))
        return f"{text}\n" if text else ''

    def _convert_rich_text(self, rich_text: List[Dict]) -> str:
        """转换富文本内容"""
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

    def _get_page_title(self, page_data: Dict) -> str:
        """获取页面标题"""
        try:
            return page_data['properties']['title']['title'][0]['plain_text']
        except (KeyError, IndexError):
            return "Untitled"

    def _handle_table(self, data: Dict, block_id: str, children: List[Dict]) -> str:
        """处理表格，包括表头和对齐方式"""
        if not children:
            return "<!-- Empty table -->\n"

        # 获取表格行数据
        rows = []
        header_row = None

        for row in children:
            if row['type'] != 'table_row':
                continue

            cells = []
            for cell in row['table_row']['cells']:
                cell_text = self._convert_rich_text(cell)
                # 转义表格中的管道符号
                cell_text = cell_text.replace('|', '\\|')
                cells.append(cell_text)

            if header_row is None:
                header_row = cells
            else:
                rows.append(cells)

        if not header_row:
            return "<!-- Invalid table structure -->\n"

        # 构建Markdown表格
        markdown_lines = []

        # 添加表头
        markdown_lines.append("| " + " | ".join(header_row) + " |")

        # 添加对齐行
        align_row = ["---"] * len(header_row)
        markdown_lines.append("| " + " | ".join(align_row) + " |")

        # 添加数据行
        for row in rows:
            # 确保每行的列数与表头一致
            while len(row) < len(header_row):
                row.append("")
            markdown_lines.append("| " + " | ".join(row) + " |")

        return "\n".join(markdown_lines) + "\n\n"

class SyncLogger:
    """同步日志管理器"""

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sync.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("NotionGitSync")

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def warning(self, message: str):
        self.logger.warning(message)


class NotionGitSync:
    """Notion和GitHub同步工具"""

    def __init__(self, config_path: str = None):
        self.config = Config(config_path)
        self.logger = SyncLogger()

        # 初始化Notion Api客户端
        self.notion = NotionClient(auth=self.config.notion_token)
        self.github = Github(self.config.github_token)

        self.converter = ContentConvert()

        self.logger.info("NotionGitSync initialized")

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_notion_content(self):
        """递归获取 Notion 内容"""
        try:
            self.logger.info(f"Fetching content from Notion page {self.config.notion_page_id}")
            # 获取根页面
            root_page = self.notion.pages.retrieve(self.config.notion_page_id)

            # 获取块信息
            blocks = self.notion.blocks.children.list(self.config.notion_page_id)

            # 递归获取所有内容
            content = {
                'page': root_page,
                'blocks': self._get_all_blocks(self.config.notion_page_id)
            }

            return content
        except Exception as e:
            self.logger.error(f"Error getting Notion content: {str(e)}")
            raise

    def _get_all_blocks(self, block_id: str) -> List[Dict]:
        blocks = []
        try:
            # 获取当前页面的所有块
            response = self.notion.blocks.children.list(block_id)
            blocks = response['results']

            # 递归获取所有有子项的块的内容
            for block in blocks:
                if block.get('has_children', False):  # 检查是否有子项
                    # 获取子块
                    child_id = block['id']
                    child_blocks = self._get_all_blocks(child_id)
                    # 保存子块
                    block['children'] = {
                        'results': child_blocks
                    }

                    # 如果是child_page类型,还需要获取页面信息
                    if block['type'] == 'child_page':
                        child_page = self.notion.pages.retrieve(child_id)
                        block['page_info'] = child_page

            return blocks

        except Exception as e:
            self.logger.error(f"Error getting blocks for {block_id}: {str(e)}")
            return blocks

    def update_github(self, file_path: str, content: str):
        try:
            repo = self.github.get_repo(self.config.github_repo)

            # 标准化路径
            file_path = file_path.replace(os.sep, '/')
            if not file_path.startswith('notion_sync/'):
                file_path = f"notion_sync/{file_path}"

            # 确保父目录存在
            dir_path = os.path.dirname(file_path)
            try:
                repo.get_contents(dir_path)
            except:
                # 创建父目录
                repo.create_file(
                    f"{dir_path}/README.md",
                    f"Create directory {dir_path}",
                    f"# {os.path.basename(dir_path)}\n"
                )

            # 更新或创建文件
            try:
                file = repo.get_contents(file_path)
                repo.update_file(
                    file_path,
                    f"Update from Notion {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    content,
                    file.sha
                )
                self.logger.info(f"Updated file {file_path}")
                self._update_sync_log(repo, "update", file_path)
            except:
                repo.create_file(
                    file_path,
                    f"Create from Notion {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    content
                )
                self.logger.info(f"Created file {file_path}")
                self._update_sync_log(repo, "create", file_path)

        except Exception as e:
            self.logger.error(f"Error updating Github: {str(e)}")
            raise

    def _update_sync_log(self, repo, action: str, file_path: str):
        """更新同步日志"""
        readme_path = "notion_sync/README.md"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            # 尝试读取现有的 README
            readme = repo.get_contents(readme_path)
            current_content = readme.decoded_content.decode()
        except:
            # 如果不存在，创建新的
            current_content = "# Notion Sync Log\n\n"

        # 添加新的同步记录
        new_log = f"- {now}: {action} `{file_path}`\n"
        updated_content = current_content + new_log

        # 更新或创建 README
        if 'readme' in locals():
            repo.update_file(
                readme_path,
                f"Update sync log {now}",
                updated_content,
                readme.sha
            )
        else:
            repo.create_file(
                readme_path,
                f"Create sync log",
                updated_content
            )

    def sync(self) -> None:
        """执行同步操作"""
        try:
            # 获取Notion内容
            notion_content = self.get_notion_content()
            if not notion_content:
                self.logger.warning("No content fetched from Notion")
                return

            # 转换内容
            base_path = self.config.base_path
            files = self.converter.convert_workspace(notion_content, base_path)
            # 更新到GitHub
            for file_path, content in files:
                self.update_github(file_path, content)

            self.logger.info("Sync completed successfully")

        except Exception as e:
            self.logger.error(f"Sync failed: {str(e)}")

    def run(self) -> None:
        """执行单次同步"""
        self.logger.info("Starting sync process")
        try:
            self.sync()
        except Exception as e:
            self.logger.error(f"Sync failed: {str(e)}")
            raise  # 重新抛出异常，让GitHub Actions知道任务失败


def main():
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description='Notion to GitHub sync tool')
    parser.add_argument('--config', type=str, help='Path to config file')
    args = parser.parse_args()

    try:
        syncer = NotionGitSync(config_path=args.config)
        syncer.run()  # 单次执行同步
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
