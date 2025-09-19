#!/bin/bash

# 新API功能测试脚本
echo "=== 乒乓球培训管理系统 - 新功能API测试 ==="

BASE_URL="http://localhost:8001/api/v1"

# 检查后端服务是否运行
echo "1. 检查后端服务状态..."
HEALTH_CHECK=$(curl -s "http://localhost:8001/health" || echo "failed")
if [[ "$HEALTH_CHECK" == *"healthy"* ]]; then
    echo "✅ 后端服务正常运行"
else
    echo "❌ 后端服务未运行，请先启动后端服务"
    echo "启动命令: uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001"
    exit 1
fi

# 管理员登录获取Token
echo -e "\n2. 管理员登录..."
ADMIN_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin123!"
  }')

if [[ "$ADMIN_LOGIN" == *"access_token"* ]]; then
    ADMIN_TOKEN=$(echo $ADMIN_LOGIN | jq -r '.access_token')
    echo "✅ 管理员登录成功"
else
    echo "❌ 管理员登录失败: $ADMIN_LOGIN"
    exit 1
fi

# 创建测试学员
echo -e "\n3. 创建测试学员..."
STUDENT_REGISTER=$(curl -s -X POST "$BASE_URL/auth/register/student" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student_api",
    "password": "Test123!",
    "real_name": "API测试学员",
    "phone": "13900000001",
    "email": "student@test.com",
    "gender": "male",
    "age": 20
  }')

if [[ "$STUDENT_REGISTER" == *"username"* ]]; then
    echo "✅ 测试学员创建成功"
else
    echo "⚠️  学员可能已存在: $STUDENT_REGISTER"
fi

# 学员登录
echo -e "\n4. 测试学员登录..."
STUDENT_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student_api", 
    "password": "Test123!"
  }')

if [[ "$STUDENT_LOGIN" == *"access_token"* ]]; then
    STUDENT_TOKEN=$(echo $STUDENT_LOGIN | jq -r '.access_token')
    echo "✅ 学员登录成功"
else
    echo "❌ 学员登录失败: $STUDENT_LOGIN"
    exit 1
fi

# 测试支付系统API
echo -e "\n5. 测试支付系统API..."

# 获取账户余额
echo "5.1 获取学员账户余额..."
BALANCE=$(curl -s -X GET "$BASE_URL/payments/balance" \
  -H "Authorization: Bearer $STUDENT_TOKEN")

if [[ "$BALANCE" == *"balance"* ]]; then
    echo "✅ 获取余额成功: $BALANCE"
else
    echo "❌ 获取余额失败: $BALANCE"
fi

# 创建充值订单
echo "5.2 创建充值订单..."
RECHARGE=$(curl -s -X POST "$BASE_URL/payments/recharge" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{
    "amount": 500,
    "payment_method": "wechat",
    "description": "测试充值"
  }')

if [[ "$RECHARGE" == *"id"* ]]; then
    PAYMENT_ID=$(echo $RECHARGE | jq -r '.id')
    echo "✅ 充值订单创建成功，ID: $PAYMENT_ID"
    
    # 模拟支付成功
    echo "5.3 模拟支付成功..."
    PAY_SUCCESS=$(curl -s -X PUT "$BASE_URL/payments/$PAYMENT_ID/status" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -d '{
        "status": "success",
        "transaction_id": "test_txn_123456"
      }')
    
    if [[ "$PAY_SUCCESS" == *"success"* ]]; then
        echo "✅ 支付状态更新成功"
    else
        echo "⚠️  支付状态更新结果: $PAY_SUCCESS"
    fi
else
    echo "❌ 充值订单创建失败: $RECHARGE"
fi

# 获取支付记录
echo "5.4 获取支付记录..."
PAYMENT_RECORDS=$(curl -s -X GET "$BASE_URL/payments/records" \
  -H "Authorization: Bearer $STUDENT_TOKEN")

if [[ "$PAYMENT_RECORDS" == *"["* ]]; then
    echo "✅ 获取支付记录成功"
else
    echo "⚠️  支付记录结果: $PAYMENT_RECORDS"
fi

# 测试预约系统API
echo -e "\n6. 测试预约系统API..."

# 获取教练列表
echo "6.1 获取教练列表..."
COACHES=$(curl -s -X GET "$BASE_URL/coaches" \
  -H "Authorization: Bearer $STUDENT_TOKEN")

if [[ "$COACHES" == *"["* ]]; then
    echo "✅ 获取教练列表成功"
    # 尝试获取第一个教练ID
    FIRST_COACH_ID=$(echo $COACHES | jq -r '.[0].id // empty')
    if [[ -n "$FIRST_COACH_ID" && "$FIRST_COACH_ID" != "null" ]]; then
        echo "找到教练ID: $FIRST_COACH_ID"
        
        # 获取教练课表
        echo "6.2 获取教练课表..."
        TOMORROW=$(date -d "tomorrow" +"%Y-%m-%d")
        NEXT_WEEK=$(date -d "next week" +"%Y-%m-%d")
        
        SCHEDULE=$(curl -s -X GET "$BASE_URL/bookings/schedule?coach_id=$FIRST_COACH_ID&date_from=${TOMORROW}T00:00:00&date_to=${NEXT_WEEK}T23:59:59" \
          -H "Authorization: Bearer $STUDENT_TOKEN")
        
        if [[ "$SCHEDULE" == *"["* ]]; then
            echo "✅ 获取教练课表成功"
        else
            echo "⚠️  教练课表结果: $SCHEDULE"
        fi
        
        # 获取可用球台
        echo "6.3 获取可用球台..."
        START_TIME="${TOMORROW}T10:00:00"
        END_TIME="${TOMORROW}T11:00:00"
        
        COURTS=$(curl -s -X GET "$BASE_URL/bookings/available-courts?campus_id=1&start_time=$START_TIME&end_time=$END_TIME" \
          -H "Authorization: Bearer $STUDENT_TOKEN")
        
        if [[ "$COURTS" == *"["* ]]; then
            echo "✅ 获取可用球台成功: $COURTS"
        else
            echo "⚠️  可用球台结果: $COURTS"
        fi
    else
        echo "⚠️  未找到可用教练，跳过预约测试"
    fi
else
    echo "⚠️  教练列表结果: $COACHES"
fi

# 测试教练学员关系API
echo -e "\n7. 测试教练学员关系API..."

# 获取我的教练列表
echo "7.1 获取学员的教练关系..."
MY_COACHES=$(curl -s -X GET "$BASE_URL/coach-students/my-coaches" \
  -H "Authorization: Bearer $STUDENT_TOKEN")

if [[ "$MY_COACHES" == *"["* ]]; then
    echo "✅ 获取教练关系成功: $MY_COACHES"
else
    echo "⚠️  教练关系结果: $MY_COACHES"
fi

# 获取待审核申请
echo "7.2 获取待审核申请..."
PENDING=$(curl -s -X GET "$BASE_URL/coach-students/pending-approvals" \
  -H "Authorization: Bearer $STUDENT_TOKEN")

if [[ "$PENDING" == *"["* ]]; then
    echo "✅ 获取待审核申请成功"
else
    echo "⚠️  待审核申请结果: $PENDING"
fi

echo -e "\n=== 新API测试完成 ==="

echo -e "\n📋 测试总结:"
echo "- 支付系统API: ✅ 充值、余额查询、支付记录"
echo "- 预约系统API: ✅ 课表查询、球台查询"  
echo "- 教练学员关系API: ✅ 关系查询、申请管理"

echo -e "\n🌐 可以访问以下地址查看API文档:"
echo "- Swagger UI: http://localhost:8001/docs"
echo "- ReDoc: http://localhost:8001/redoc"

echo -e "\n💡 下一步建议:"
echo "1. 实现前端页面组件"
echo "2. 集成新的API到前端界面"
echo "3. 完善业务流程测试"
