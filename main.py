import logging
import os
from datetime import datetime
from typing import Dict, List

import time

from notion_client import Client as NotionClient
from github import Github
import schedule
import yaml
from retrying import retry


class Config:
    """配置管理类"""
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.getenv("CONFIG_PATH", "config.yml")
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, "r", encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to load config: {str(e)}")

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
        self.list_indent_level = 0
        self.table_data = {}  # 用于缓存表格数据

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

    def notion_to_markdown(self, notion_content: Dict) -> str:
        """将Notion内容转换为Markdown格式

        Args:
            notion_content (Dict): 包含page和blocks的Notion内容

        Returns:
            str: 转换后的Markdown文本
        """
        page = notion_content['page']
        blocks = notion_content['blocks']

        # 处理页面标题
        title = notion_content['page']['properties']['title']['title'][0]['plain_text']

        # 生成markdown内容
        markdown_lines = [
            f"# {title}",
            f"\n_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n",
            "---\n"
        ]

        # 处理所有块
        for block in notion_content['blocks']['results']:
            # 根据块类型进行处理
            block_type = block['type']
            if block_type == 'child_page':
                # 处理子页面
                page_title = block['child_page']['title']
                markdown_lines.append(f"## [{page_title}](notion://{block['id']})\n")
            elif block_type == 'paragraph':
                # 处理段落
                text = []
                for rich_text in block['paragraph'].get('rich_text', []):
                    if 'plain_text' in rich_text:
                        text.append(rich_text['plain_text'])
                if text:
                    markdown_lines.append(' '.join(text) + '\n')

        return '\n'.join(markdown_lines)

    def _convert_block_with_children(self, block: Dict) -> str:
        """转换块及其子块"""
        block_content = self._convert_block(block)

        # 处理子块
        if block.get('has_children') and 'children' in block:
            child_contents = []
            # 增加缩进级别
            self.list_indent_level += 1

            for child in block['children']:
                child_content = self._convert_block_with_children(child)
                if child_content:
                    child_contents.append(child_content)

            # 恢复缩进级别
            self.list_indent_level -= 1

            # 特殊处理表格的子块
            if block['type'] == 'table':
                block_content = self._handle_table(
                    block[block['type']],
                    block['id'],
                    block['children']
                )
            else:
                block_content = block_content + "\n".join(child_contents)

        return block_content

    def _convert_table_cell(self, cell: List[Dict]) -> str:
        """转换表格单元格内容"""
        text = self._convert_rich_text(cell)
        # 转义特殊字符
        text = text.replace('\n', '<br>')
        text = text.replace('|', '\\|')
        return text or " "

    def _get_page_title(self, page: Dict) -> str:
        """获取页面标题"""
        try:
            return self._convert_rich_text(page['properties']['title']['title'])
        except :
            return "Untitled"

    def _convert_block(self, block: Dict) -> str:
        """转换单个块为Markdown

        处理不同类型的块并返回对应的Markdown文本
        """
        block_type = block['type']
        block_handler = getattr(self, f"_handle_{block_type}", self._handle_unsupported)
        return block_handler(block[block_type])

    def _convert_rich_text(self, rich_text: List[Dict]) -> str:
        """转换富文本格式"""
        if not rich_text:
            return ""

        result = []
        for text in rich_text:
            content = text.get('plain_text', '')
            annotations = text.get('annotations', {})
            href = text.get('href', '')

            # 应用文本格式
            if annotations.get('code'):
                content = f'`{content}`'
            if annotations.get('bold'):
                content = f'**{content}**'
            if annotations.get('italic'):
                content = f'_{content}_'
            if annotations.get('strikethrough'):
                content = f'~~{content}~~'
            if href:
                content = f'[{content}]({href})'

            result.append(content)

        return ''.join(result)

    def _handle_paragraph(self, data: Dict) -> str:
        """处理段落"""
        text = self._convert_rich_text(data.get('rich_text', []))
        return f"{text}\n"

    def _handle_heading_1(self, data: Dict) -> str:
        """处理一级标题"""
        text = self._convert_rich_text(data.get('rich_text', []))
        return f"# {text}\n"

    def _handle_heading_2(self, data: Dict) -> str:
        """处理二级标题"""
        text = self._convert_rich_text(data.get('rich_text', []))
        return f"## {text}\n"

    def _handle_heading_3(self, data: Dict) -> str:
        """处理三级标题"""
        text = self._convert_rich_text(data.get('rich_text', []))
        return f"### {text}\n"

    def _handle_bulleted_list_item(self, data: Dict) -> str:
        """处理无序列表项"""
        text = self._convert_rich_text(data.get('rich_text', []))
        indent = "  " * self.list_indent_level
        return f"{indent}- {text}\n"

    def _handle_numbered_list_item(self, data: Dict) -> str:
        """处理有序列表项"""
        text = self._convert_rich_text(data.get('rich_text', []))
        indent = "  " * self.list_indent_level
        return f"{indent}1. {text}\n"

    def _handle_to_do(self, data: Dict) -> str:
        """处理待办事项"""
        text = self._convert_rich_text(data.get('rich_text', []))
        checked = data.get('checked', False)
        checkbox = "[x]" if checked else "[ ]"
        return f"- {checkbox} {text}\n"

    def _handle_code(self, data: Dict) -> str:
        """处理代码块"""
        text = self._convert_rich_text(data.get('rich_text', []))
        language = data.get('language', '')
        return f"```{language}\n{text}\n```\n"

    def _handle_quote(self, data: Dict) -> str:
        """处理引用"""
        text = self._convert_rich_text(data.get('rich_text', []))
        return f"> {text}\n"

    def _handle_callout(self, data: Dict) -> str:
        """处理高亮块"""
        text = self._convert_rich_text(data.get('rich_text', []))
        icon = data.get('icon', {}).get('emoji', 'ℹ️')
        return f"> {icon} **Note**\n> {text}\n"

    def _handle_image(self, data: Dict) -> str:
        """处理图片
        暂时只处理外部图片链接
        """
        caption = self._convert_rich_text(data.get('caption', []))
        if 'external' in data:
            url = data['external'].get('url', '')
            return f"![{caption}]({url})\n"
        elif 'file' in data:
            url = data['file'].get('url', '')
            return f"![{caption}]({url})\n"
        return ''

    def _handle_table(self, data: Dict) -> str:
        """处理表格
        需要获取表格的子块来构建完整表格
        """
        # TODO: 实现表格处理
        return "<!-- Table content not implemented yet -->\n"

    def _handle_divider(self, _: Dict) -> str:
        """处理分割线"""
        return "---\n"

    def _handle_unsupported(self, _: Dict) -> str:
        """处理未支持的块类型"""
        return "<!-- Unsupported content type -->\n"

    def _handle_child_page(self, data: Dict) -> str:
        """处理子页面引用"""
        title = data.get('title', 'Untitled')
        return f"[[{title}]]\n"

    def _handle_bookmark(self, data: Dict) -> str:
        """处理书签"""
        url = data.get('url', '')
        caption = self._convert_rich_text(data.get('caption', []))
        return f"[{caption or url}]({url})\n"

    def _handle_equation(self, data: Dict) -> str:
        """处理数学公式"""
        expression = data.get('expression', '')
        return f"$${expression}$$\n"

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
        """从Notion获取内容，失败时重试"""
        try:
            self.logger.info(f"Fetching content from Notion page {self.config.notion_page_id}")
            # 获取页面信息
            page = self.notion.pages.retrieve(self.config.notion_page_id)
            # 递归获取所有块
            blocks = self.notion.blocks.children.list(self.config.notion_page_id)

            content = {
                'page': page,
                'blocks': blocks
            }

            self.logger.info(f"Successfully fetched content from Notion: {content}")
            return content
        except Exception as e:
            print(f"Error getting Notion content: {e}")
            return

    def _get_all_blocks(self, block_id: str) -> List[Dict]:
        """递归获取所有块及其子块"""
        blocks = []
        try:
            response = self.notion.blocks.children.list(block_id)
            for block in response['results']:
                blocks.append(block)

                # 处理可能包含子块的块类型
                if block['has_children']:
                    child_blocks = self._get_all_blocks(block['id'])
                    block['children'] = child_blocks

            return blocks
        except Exception as e:
            self.logger.error(f"Error getting blocks for {block_id}: {str(e)}")
            return blocks

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def update_github(self, content):
        """更新GitHub仓库，失败时重试"""
        try:
            repo = self.github.get_repo(self.config.github_repo)
            # 生成文件路径和名称
            timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
            file_path = os.path.join(
                self.config.base_path,
                f"{timestamp}.md"
            )

            try:
                file = repo.get_contents(file_path)
                repo.update_file(
                    file_path,
                    f"Update from Notion {timestamp}",
                    content,
                    file.sha
                )
                self.logger.info(f"Updated file {file_path} in GitHub")
            except Exception:
                repo.create_file(
                    file_path,
                    f"Create from Notion {timestamp}",
                    content
                )
                self.logger.info(f"Created file {file_path} in GitHub")

        except Exception as e:
            self.logger.error(f"Error updating Github: {str(e)}")
            raise

    def sync(self) -> None:
        """执行同步操作"""
        try:
            # 获取Notion内容
            notion_content = self.get_notion_content()
            if not notion_content:
                self.logger.warning("No content fetched from Notion")
                return

            # 转换内容格式
            markdown_content = self.converter.notion_to_markdown(notion_content)
            # 更新到GitHub
            self.update_github(markdown_content)

            self.logger.info("Sync completed successfully")

        except Exception as e:
            self.logger.error(f"Sync failed: {str(e)}")

    def run(self) -> None:
        """运行同步服务"""
        self.logger.info(f"Starting sync service with {self.config.sync_interval} minutes interval")

        # 设置定时任务
        schedule.every(self.config.sync_interval).minutes.do(self.sync)

        # 先执行一次同步
        self.sync()

        # 运行定时任务
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                self.logger.info("Sync service stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                # 休息一段时间后继续
                time.sleep(300)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Notion to GitHub sync tool')
    parser.add_argument('--config', type=str, help='Path to config file')
    args = parser.parse_args()

    syncer = NotionGitSync(args.config)
    syncer.run()

if __name__ == '__main__':
    main()