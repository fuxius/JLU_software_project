"""
用户管理功能测试脚本
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_user_management():
    print("=== 用户管理API测试 ===")
    
    # 1. 登录获取token
    print("1. 测试用户登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✓ 登录成功，获取到token")
        else:
            print(f"✗ 登录失败: {response.status_code} - {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务器，请确保服务器已启动")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 测试获取用户列表
    print("\n2. 测试获取用户列表...")
    try:
        response = requests.get(f"{BASE_URL}/users/?skip=0&limit=10", headers=headers)
        if response.status_code == 200:
            users_data = response.json()
            print(f"✓ 成功获取用户列表，共 {users_data.get('total', 0)} 个用户")
            print(f"   当前页显示 {len(users_data.get('items', []))} 个用户")
        else:
            print(f"✗ 获取用户列表失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 获取用户列表异常: {e}")
    
    # 3. 测试搜索用户
    print("\n3. 测试搜索用户...")
    try:
        response = requests.get(f"{BASE_URL}/users/?username=admin", headers=headers)
        if response.status_code == 200:
            users_data = response.json()
            print(f"✓ 搜索成功，找到 {users_data.get('total', 0)} 个匹配用户")
        else:
            print(f"✗ 搜索用户失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 搜索用户异常: {e}")
    
    # 4. 测试获取单个用户信息
    print("\n4. 测试获取单个用户信息...")
    try:
        response = requests.get(f"{BASE_URL}/users/1", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ 成功获取用户信息: {user_data.get('username')} - {user_data.get('real_name')}")
        else:
            print(f"✗ 获取用户信息失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 获取用户信息异常: {e}")
    
    # 5. 测试重置密码
    print("\n5. 测试重置用户密码...")
    try:
        response = requests.post(f"{BASE_URL}/users/1/reset-password", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 密码重置成功，新密码: {result.get('new_password')}")
        else:
            print(f"✗ 重置密码失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 重置密码异常: {e}")
    
    # 6. 测试切换用户状态
    print("\n6. 测试切换用户状态...")
    try:
        response = requests.patch(f"{BASE_URL}/users/1/toggle-status", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 状态切换成功: {result.get('message')}")
        else:
            print(f"✗ 切换状态失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 切换状态异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_user_management()