import os
from github import Github

# 从环境变量获取 token
token = os.getenv('GITHUB_TOKEN') or os.getenv('ACTIONS_TOKEN')
if not token:
    print("❌ No token found in environment variables")
    exit(1)

print("Testing GitHub token permissions...")

try:
    # 初始化 GitHub 客户端
    g = Github(token)
    
    # 获取当前用户
    user = g.get_user()
    print(f"✅ Authenticated as: {user.login}")
    
    # 测试对各个仓库的访问权限
    repos_to_test = [
        "HyxiaoGe/notion-notes",
        "HyxiaoGe/blog",
        "HyxiaoGe/hyxiaoge.github.io"
    ]
    
    for repo_name in repos_to_test:
        try:
            repo = g.get_repo(repo_name)
            print(f"✅ Can access: {repo_name}")
            
            # 测试写入权限
            try:
                # 尝试获取一个不存在的文件（不会实际创建）
                repo.get_contents("test-permission-check.txt")
            except:
                # 404 错误是正常的，说明有读取权限
                print(f"✅ Has read permission for: {repo_name}")
                
            # 检查是否可以推送
            if repo.permissions.push:
                print(f"✅ Can push to: {repo_name}")
            else:
                print(f"❌ Cannot push to: {repo_name}")
                
        except Exception as e:
            print(f"❌ Cannot access {repo_name}: {str(e)}")
    
    print("\n✅ Token validation complete!")
    
except Exception as e:
    print(f"❌ Authentication failed: {str(e)}")
    print("\nMake sure your token has 'repo' scope enabled")