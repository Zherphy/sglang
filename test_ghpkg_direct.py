#!/usr/bin/env python3
"""
直接测试 GitHub Packages Python 上传的脚本
用于验证正确的 URL 格式和端点
"""

import os
import requests
import json
from urllib.parse import urljoin

def test_github_packages_urls():
    """测试不同的 GitHub Packages URL 格式"""
    
    # 从环境变量获取 token
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN 未设置")
        return
    
    owner = "Zherphy"
    repo = "sglang"
    package_name = "sglang"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    print("=== 测试 GitHub Packages URL 格式 ===")
    print(f"Owner: {owner}")
    print(f"Repository: {repo}")
    print(f"Package name: {package_name}")
    print()
    
    # 测试不同的 URL 格式
    test_urls = [
        # 格式 1: 使用 upload.pkg.github.com
        f"https://upload.pkg.github.com/{owner}/{package_name}",
        f"https://upload.pkg.github.com/{owner}/{repo}",
        
        # 格式 2: 使用 api.github.com/user/packages
        f"https://api.github.com/user/packages?package_type=pypi",
        
        # 格式 3: 检查包是否存在
        f"https://api.github.com/user/packages/pypi/{package_name}",
        
        # 格式 4: 使用 pkg.github.com
        f"https://pkg.github.com/{owner}/{package_name}/simple",
    ]
    
    for url in test_urls:
        print(f"\n测试 URL: {url}")
        print("-" * 50)
        
        try:
            if "api.github.com" in url:
                response = requests.get(url, headers=headers)
            else:
                response = requests.head(url, headers=headers)
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ URL 可访问")
            elif response.status_code == 404:
                print("❌ 404 Not Found - URL 不存在")
            elif response.status_code == 403:
                print("⚠️  403 Forbidden - 权限不足")
            else:
                print(f"⚠️  其他状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    print("\n=== 检查现有包 ===")
    # 检查用户已有的包
    packages_url = f"https://api.github.com/user/packages?package_type=pypi"
    try:
        response = requests.get(packages_url, headers=headers)
        if response.status_code == 200:
            packages = response.json()
            if packages:
                print("已有的 Python 包:")
                for pkg in packages:
                    print(f"  - {pkg.get('name')} (可见性: {pkg.get('visibility')})")
            else:
                print("没有找到 Python 包")
        else:
            print(f"获取包列表失败: {response.status_code}")
    except Exception as e:
        print(f"获取包列表失败: {e}")
    
    print("\n=== GitHub Packages 文档参考 ===")
    print("根据 GitHub 官方文档:")
    print("1. Python 包上传: https://upload.pkg.github.com/OWNER/")
    print("   注意：有些文档显示为 https://upload.pkg.github.com/OWNER/REPO")
    print("2. 安装: https://pkg.github.com/OWNER/REPO/simple")
    print()
    print("=== 可能的解决方案 ===")
    print("1. 尝试使用不同的 URL 格式")
    print("2. 检查 GitHub Packages 是否已启用")
    print("3. 检查 token 权限 (需要 packages:write)")
    print("4. 尝试先通过 Web UI 创建包")

if __name__ == "__main__":
    test_github_packages_urls()