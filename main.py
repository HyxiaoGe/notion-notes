from datetime import datetime

import schedule
import time
from notion_client import Client
from github import Github
import yaml


class NotionGitSync:
    def __init__(self, config_path='config.yml'):
        # 加载配置
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # 初始化Notion Api客户端
        self.notion = Client(auth=config['notion_token'])
        self.github = Github(config['github_token'])

        # 配置参数
        self.notion_page_id = config['notion_page_id']
        self.github_repo = config['github_repo']
        self.sync_interval = config['sync_interval']

    def get_notion_content(self):
        """从Notion获取内容"""
        try:
            page = self.notion.pages.retrieve(self.notion_page_id)

            return page
        except Exception as e:
            print(f"Error getting Notion content: {e}")
            return None

    def update_github(self, content):
        """更新GitHub仓库"""
        try:
            repo = self.github.get_repo(self.github_repo)
            # 获取/创建文件
            file_path = f"notion_sync/{datetime.now().strftime('%Y-%m-%d')}.md"

            try:
                file = repo.get_contents(file_path)
                repo.update_file(
                    file_path,
                    f"Update from Notion {datetime.now()}",
                    content,
                    file.sha
                )
            except:
                repo.create_file(
                    file_path,
                    f"Create from Notion {datetime.now()}",
                    content
                )

        except Exception as e:
            print(f"Error updating Github: {e}")

def main():
    syncer = NotionGitSync()

    # 设置定时任务
    schedule.every(syncer.sync_interval).minutes.do(syncer.sync)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main()