import os
from notion_client import Client

# 从环境变量获取配置
notion_token = os.getenv('NOTION_TOKEN')
page_id = os.getenv('NOTION_PAGE_ID')

print(f"Testing Notion connection...")
print(f"Page ID: {page_id}")

# 初始化客户端
notion = Client(auth=notion_token)

try:
    # 尝试获取页面
    page = notion.pages.retrieve(page_id)
    print(f"✅ Success! Found page: {page['properties'].get('title', {}).get('title', [{}])[0].get('plain_text', 'Untitled')}")
    print(f"Page URL: {page['url']}")
    print(f"Created: {page['created_time']}")
    print(f"Last edited: {page['last_edited_time']}")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPossible solutions:")
    print("1. Make sure the page is shared with your integration")
    print("2. Check if the Page ID is in correct UUID format (with hyphens)")
    print("3. Verify the integration has read permissions")