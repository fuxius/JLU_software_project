#!/bin/bash

# 乒乓球培训管理系统 API 测试脚本
echo "🏓 乒乓球培训管理系统 API 测试"
echo "================================"

BASE_URL="http://localhost:8001/api/v1"

# 测试健康检查
echo "1. 测试健康检查..."
curl -s http://localhost:8001/health | jq .
echo ""

# 测试学员注册
echo "2. 测试学员注册..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register/student" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student_demo",
    "password": "Demo123!",
    "real_name": "演示学员",
    "phone": "13800138888",
    "email": "student@demo.com",
    "gender": "male",
    "age": 20
  }')

echo "$REGISTER_RESPONSE" | jq .
echo ""

# 测试登录
echo "3. 测试学员登录..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student_demo",
    "password": "Demo123!"
  }')

echo "$LOGIN_RESPONSE" | jq .

# 提取token
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
echo "获取到的token: ${TOKEN:0:50}..."
echo ""

# 测试获取当前用户信息
echo "4. 测试获取当前用户信息..."
curl -s -X GET "$BASE_URL/users/me" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# 测试获取校区列表
echo "5. 测试获取校区列表..."
curl -s -X GET "$BASE_URL/campus" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# 测试获取教练列表
echo "6. 测试获取教练列表..."
curl -s -X GET "$BASE_URL/coaches" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

echo "✅ API测试完成！"
echo ""
echo "🌐 现在可以访问以下地址："
echo "- 前端: http://localhost:3001"
echo "- API文档: http://localhost:8001/docs"
echo "- 健康检查: http://localhost:8001/health"
