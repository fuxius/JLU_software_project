#!/bin/bash

echo "=== 乒乓球培训管理系统 - 双选关系流程测试 ==="

BASE_URL="http://localhost:8001/api/v1"

# 1. 注册教练
echo "1. 注册教练..."
COACH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register/coach" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "coach_zhang",
    "password": "Coach123!",
    "real_name": "张教练",
    "phone": "13800138002",
    "email": "coach@example.com",
    "gender": "male",
    "age": 30
  }')

echo "教练注册结果: $COACH_RESPONSE"

# 2. 教练登录
echo -e "\n2. 教练登录..."
COACH_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "coach_zhang",
    "password": "Coach123!"
  }')

COACH_TOKEN=$(echo $COACH_LOGIN | jq -r '.access_token')
COACH_ID=$(echo $COACH_LOGIN | jq -r '.user.id')
echo "教练Token: ${COACH_TOKEN:0:50}..."

# 3. 创建教练详细信息
echo -e "\n3. 创建教练详细信息..."
# 这里需要先实现创建教练详细信息的逻辑

# 4. 学员登录
echo -e "\n4. 学员登录..."
STUDENT_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user2",
    "password": "Test123!"
  }')

STUDENT_TOKEN=$(echo $STUDENT_LOGIN | jq -r '.access_token')
STUDENT_ID=$(echo $STUDENT_LOGIN | jq -r '.user.id')
echo "学员Token: ${STUDENT_TOKEN:0:50}..."

# 5. 查看教练列表
echo -e "\n5. 查看教练列表..."
COACHES_LIST=$(curl -s "$BASE_URL/coaches" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
echo "教练列表: $COACHES_LIST"

# 6. 学员申请选择教练
echo -e "\n6. 学员申请选择教练..."
# 这需要先获取教练的coach_id，而不是user_id

echo -e "\n=== 测试完成 ==="
echo "注意：完整的双选流程需要以下数据："
echo "1. 教练需要有对应的Coach记录"
echo "2. 学员需要有对应的Student记录"
echo "3. 需要校区数据"
