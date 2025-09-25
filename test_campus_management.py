"""
校区管理功能测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_campus_management():
    print("=== 校区管理API测试 ===")
    
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
    
    # 2. 测试获取校区列表
    print("\n2. 测试获取校区列表...")
    try:
        response = requests.get(f"{BASE_URL}/campus/?skip=0&limit=10", headers=headers)
        if response.status_code == 200:
            campuses_data = response.json()
            print(f"✓ 成功获取校区列表，共 {campuses_data.get('total', 0)} 个校区")
            print(f"   当前页显示 {len(campuses_data.get('items', []))} 个校区")
        else:
            print(f"✗ 获取校区列表失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 获取校区列表异常: {e}")
    
    # 3. 测试创建校区
    print("\n3. 测试创建校区...")
    try:
        campus_data = {
            "name": "测试校区",
            "address": "测试地址123号",
            "contact_person": "张三",
            "contact_phone": "13800138000",
            "contact_email": "test@example.com",
            "is_main_campus": False
        }
        response = requests.post(f"{BASE_URL}/campus/", json=campus_data, headers=headers)
        if response.status_code == 200:
            created_campus = response.json()
            campus_id = created_campus.get('id')
            print(f"✓ 创建校区成功，校区ID: {campus_id}")
        else:
            print(f"✗ 创建校区失败: {response.status_code} - {response.text}")
            campus_id = None
    except Exception as e:
        print(f"✗ 创建校区异常: {e}")
        campus_id = None
    
    # 4. 测试更新校区
    if campus_id:
        print("\n4. 测试更新校区...")
        try:
            update_data = {
                "name": "更新的测试校区",
                "address": "更新的测试地址456号"
            }
            response = requests.put(f"{BASE_URL}/campus/{campus_id}", json=update_data, headers=headers)
            if response.status_code == 200:
                print("✓ 校区更新成功")
            else:
                print(f"✗ 校区更新失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"✗ 校区更新异常: {e}")
    
    # 5. 测试搜索校区
    print("\n5. 测试搜索校区...")
    try:
        response = requests.get(f"{BASE_URL}/campus/?name=测试", headers=headers)
        if response.status_code == 200:
            search_result = response.json()
            print(f"✓ 搜索成功，找到 {search_result.get('total', 0)} 个匹配校区")
        else:
            print(f"✗ 搜索校区失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 搜索校区异常: {e}")
    
    # 6. 测试删除校区
    if campus_id:
        print("\n6. 测试删除校区...")
        try:
            response = requests.delete(f"{BASE_URL}/campus/{campus_id}", headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(f"✓ 删除校区成功: {result.get('message')}")
            else:
                print(f"✗ 删除校区失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"✗ 删除校区异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_campus_management()