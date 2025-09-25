#!/bin/bash

# 测试校区管理新增功能的脚本

BASE_URL="http://localhost:8000"

echo "=== 校区新增功能测试 ==="

# 1. 测试登录获取token
echo "1. 测试用户登录..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

echo "登录响应: $LOGIN_RESPONSE"

# 提取token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "登录失败，无法获取token"
    exit 1
fi

echo "获取到token: $TOKEN"

# 2. 测试创建校区
echo -e "\n2. 测试创建新校区..."
CAMPUS_DATA='{
  "name": "测试校区_自动化测试",
  "address": "测试地址123号",
  "contact_person": "测试联系人",
  "contact_phone": "13800138888",
  "contact_email": "test@example.com",
  "is_main_campus": false
}'

CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/campus/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$CAMPUS_DATA")

echo "创建校区响应: $CREATE_RESPONSE"

# 3. 测试获取校区列表验证创建结果
echo -e "\n3. 验证校区是否创建成功..."
curl -s -X GET "$BASE_URL/campus/?name=测试校区" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

echo -e "\n=== 测试完成 ==="