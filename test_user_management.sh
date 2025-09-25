#!/bin/bash

# 测试用户管理API的脚本
# 需要先启动后端服务器

BASE_URL="http://localhost:8000"

echo "=== 用户管理API测试 ==="

# 1. 测试登录获取token（需要有管理员账户）
echo "1. 测试用户登录..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

echo "登录响应: $LOGIN_RESPONSE"

# 提取token（假设响应格式为 {"access_token": "...", "token_type": "bearer"}）
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "登录失败，无法获取token"
    exit 1
fi

echo "获取到token: $TOKEN"

# 2. 测试获取用户列表
echo -e "\n2. 测试获取用户列表..."
curl -s -X GET "$BASE_URL/users/?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

# 3. 测试搜索用户
echo -e "\n3. 测试搜索用户（搜索管理员）..."
curl -s -X GET "$BASE_URL/users/?username=admin" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

# 4. 测试获取单个用户信息（假设用户ID为1）
echo -e "\n4. 测试获取单个用户信息..."
curl -s -X GET "$BASE_URL/users/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

# 5. 测试更新用户信息
echo -e "\n5. 测试更新用户信息..."
curl -s -X PUT "$BASE_URL/users/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"real_name": "更新的管理员名称", "age": 25}' | jq '.'

echo -e "\n=== 测试完成 ==="