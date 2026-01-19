#!/usr/bin/env python3
"""
直接检查 GitHub Packages API 的脚本
用于确定正确的端点和配置
"""

import os
import requests
import json

def check_github_packages():
    """检查 GitHub Packages 配置"""
    
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN 未设置")
        return
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Packages-Test"
    }
    
    print("=== 检查 GitHub Packages 配置 ===")
    print()
    
    # 1. 检查用户信息
    print("1. 检查用户信息...")
    try:
        user_response = requests.get("https://api.github.com/user", headers=headers)
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"   ✅ 用户: {user_data.get('login')}")
            print(f"   ✅ ID: {user_data.get('id')}")
        else:
            print(f"   ❌ 获取用户信息失败: {user_response.status_code}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    
    # 2. 检查已有的 Python 包
    print("2. 检查已有的 Python 包...")
    try:
        packages_response = requests.get(
            "https://api.github.com/user/packages?package_type=pypi",
            headers=headers
        )
        
        if packages_response.status_code == 200:
            packages = packages_response.json()
            if packages:
                print(f"   ✅ 找到 {len(packages)} 个 Python 包:")
                for pkg in packages:
                    print(f"      - {pkg.get('name')} (可见性: {pkg.get('visibility')})")
            else:
                print("   ℹ️  没有找到 Python 包")
        elif packages_response.status_code == 404:
            print("   ❌ 404 - 端点不存在或权限不足")
        else:
            print(f"   ❌ 获取包列表失败: {packages_response.status_code}")
            print(f"      响应: {packages_response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    
    # 3. 检查特定包是否存在
    print("3. 检查包 'sglang' 是否存在...")
    try:
        package_response = requests.get(
            "https://api.github.com/user/packages/pypi/sglang",
            headers=headers
        )
        
        if package_response.status_code == 200:
            print("   ✅ 包 'sglang' 存在")
            package_data = package_response.json()
            print(f"      名称: {package_data.get('name')}")
            print(f"      可见性: {package_data.get('visibility')}")
            print(f"      创建时间: {package_data.get('created_at')}")
        elif package_response.status_code == 404:
            print("   ❌ 包 'sglang' 不存在 (404)")
        else:
            print(f"   ❌ 检查包失败: {package_response.status_code}")
            print(f"      响应: {package_response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    
    # 4. 测试不同的上传端点
    print("4. 测试不同的上传端点...")
    
    test_endpoints = [
        "https://upload.pkg.github.com/",
        "https://upload.pkg.github.com/Zherphy/",
        "https://upload.pkg.github.com/Zherphy/sglang",
        "https://pkg.github.com/Zherphy/sglang/simple",
    ]
    
    for endpoint in test_endpoints:
        print(f"   测试: {endpoint}")
        try:
            # 使用 HEAD 请求测试端点
            head_response = requests.head(endpoint, headers=headers, timeout=5)
            print(f"      HEAD 状态码: {head_response.status_code}")
            
            # 如果是 404，尝试 GET 获取更多信息
            if head_response.status_code == 404:
                get_response = requests.get(endpoint, headers=headers, timeout=5)
                print(f"      GET 状态码: {get_response.status_code}")
                if get_response.status_code != 404:
                    print(f"      响应类型: {get_response.headers.get('content-type', 'unknown')}")
        except requests.exceptions.Timeout:
            print("      ⏱️  请求超时")
        except Exception as e:
            print(f"      ❌ 错误: {e}")
    
    print()
    
    # 5. 检查 GitHub Packages 文档中的正确格式
    print("5. GitHub Packages 文档参考:")
    print("   根据官方文档 (https://docs.github.com/en/packages):")
    print("   - Python 包上传: twine upload --repository-url https://upload.pkg.github.com/OWNER/")
    print("   - 注意: 有些版本可能需要不同的格式")
    print()
    print("6. 可能的解决方案:")
    print("   a) 确保 GitHub Packages 已为账户启用")
    print("   b) 检查 token 权限 (需要 'packages: write')")
    print("   c) 尝试先通过 Web UI 创建包")
    print("   d) 使用不同的包名 (避免冲突)")
    print("   e) 联系 GitHub 支持检查账户配置")

if __name__ == "__main__":
    check_github_packages()