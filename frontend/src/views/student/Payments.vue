<template>
  <div class="student-payments">
    <el-card>
      <template #header>
        <span>账户充值</span>
      </template>
      
      <div class="balance-info">
        <h3>当前余额：<span class="balance">￥{{ balance }}</span></h3>
      </div>
      
      <el-form :model="paymentForm" label-width="100px">
        <el-form-item label="充值金额">
          <el-input-number v-model="paymentForm.amount" :min="1" :max="10000" />
        </el-form-item>
        <el-form-item label="支付方式">
          <el-radio-group v-model="paymentForm.method" size="default">
            <el-radio label="wechat">微信支付</el-radio>
            <el-radio label="alipay">支付宝</el-radio>
            <el-radio label="offline">线下支付</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handlePayment">充值</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>账户流水</span>
          <el-radio-group v-model="recordType" size="small" @change="filterRecords">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="recharge">充值</el-radio-button>
            <el-radio-button label="expense">消费</el-radio-button>
            <el-radio-button label="refund">退款</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <el-table :data="filteredPaymentHistory" stripe>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="scope">
            <span :class="getAmountClass(scope.row.type, scope.row.payment_method)">
              {{ formatAmount(scope.row.amount, scope.row.type, scope.row.payment_method) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="支付方式" width="120">
          <template #default="scope">
            {{ getPaymentMethodText(scope.row.payment_method, scope.row.type) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="备注" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { paymentApi } from '@/api/payments'

const balance = ref(0)
const paymentForm = reactive({
  amount: 100,
  method: 'wechat' as 'wechat' | 'alipay' | 'offline'
})
const paymentHistory = ref<any[]>([])
const recordType = ref('all')

// 计算属性：过滤后的支付记录
const filteredPaymentHistory = computed(() => {
  if (recordType.value === 'all') {
    return paymentHistory.value
  } else if (recordType.value === 'expense') {
    // 消费类型包括课程费用和比赛报名费
    return paymentHistory.value.filter(item => 
      ['booking', 'competition'].includes(item.type)
    )
  } else {
    return paymentHistory.value.filter(item => item.type === recordType.value)
  }
})

// 获取记录类型文本
const getRecordTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    'recharge': '充值',
    'booking': '课程费用',
    'competition': '比赛报名费',
    'refund': '退款'
  }
  return typeMap[type] || type
}

// 获取记录标签类型
const getRecordTagType = (type: string) => {
  const tagMap: Record<string, string> = {
    'recharge': 'success',
    'booking': 'warning',
    'competition': 'info',
    'refund': 'primary'
  }
  return tagMap[type] || 'default'
}

// 格式化金额显示
const formatAmount = (amount: number, type: string, paymentMethod: string) => {
  // 根据支付方式判断：balance支付显示负数，其他支付方式显示正数
  if (paymentMethod === 'balance') {
    return `-￥${Math.abs(amount)}`
  } else {
    return `+￥${Math.abs(amount)}`
  }
}

// 获取金额样式类
const getAmountClass = (type: string, paymentMethod: string) => {
  return paymentMethod === 'balance' ? 'amount-negative' : 'amount-positive'
}

// 获取支付方式文本
const getPaymentMethodText = (paymentMethod: string, type: string) => {
  if (!paymentMethod) {
    // 如果是消费类型且没有支付方式，显示"余额支付"
    if (['booking', 'competition'].includes(type)) {
      return '余额支付'
    }
    return '-'
  }
  
  const methodMap: Record<string, string> = {
    'wechat': '微信支付',
    'alipay': '支付宝',
    'offline': '线下支付',
    'balance': '余额支付'
  }
  return methodMap[paymentMethod] || paymentMethod
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待支付',
    'success': '成功',
    'failed': '失败',
    'cancelled': '已取消',
    'refunded': '已退款'
  }
  return statusMap[status] || status
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  const tagMap: Record<string, string> = {
    'pending': 'warning',
    'success': 'success',
    'failed': 'danger',
    'cancelled': 'info',
    'refunded': 'primary'
  }
  return tagMap[status] || 'default'
}

// 过滤记录
const filterRecords = () => {
  // 切换筛选类型时自动触发计算属性更新
}

const loadBalance = async () => {
  try {
    // 调用获取余额API
    const result: any = await paymentApi.getBalance()
    balance.value = result.balance || 0
  } catch (error) {
    console.error('加载余额失败:', error)
    ElMessage.error('加载余额失败')
    // 如果API失败，使用默认值
    balance.value = 500
  }
}

const loadPaymentHistory = async () => {
  try {
    // 调用获取充值记录API
    const result: any = await paymentApi.getPaymentRecords()
    paymentHistory.value = result || []
  } catch (error) {
    console.error('加载支付记录失败:', error)
    ElMessage.error('加载支付记录失败')
    // 如果API失败，使用默认数据
    paymentHistory.value = [
      {
        id: 1,
        type: 'recharge',
        amount: 200,
        payment_method: 'wechat',
        status: 'success',
        description: '账户充值',
        created_at: '2024-01-10 10:30:00'
      },
      {
        id: 2,
        type: 'booking',
        amount: 150,
        payment_method: 'balance',
        status: 'success',
        description: '预约教练课程',
        created_at: '2024-01-11 14:20:00'
      }
    ]
  }
}

const handlePayment = async () => {
  if (!paymentForm.amount || paymentForm.amount <= 0) {
    ElMessage.error('请输入有效的充值金额')
    return
  }

  try {
    // 调用实际的充值API
    const rechargeData = {
      amount: paymentForm.amount,
      payment_method: paymentForm.method,
      description: '账户充值'
    }

    const result = await paymentApi.recharge(rechargeData)

    ElMessage.success(`充值${paymentForm.amount}元成功`)

    // 刷新余额和充值记录
    await loadBalance()
    await loadPaymentHistory()

    // 重置表单
    paymentForm.amount = 100
    paymentForm.method = 'wechat'
  } catch (error: any) {
    console.error('充值失败:', error)
    ElMessage.error(error.message || '充值失败，请重试')
  }
}

onMounted(() => {
  loadBalance()
  loadPaymentHistory()
})
</script>

<style scoped>
.balance-info {
  margin-bottom: 20px;
}

.balance {
  color: #67c23a;
  font-size: 24px;
  font-weight: bold;
}

.amount-positive {
  color: #67c23a;
  font-weight: bold;
}

.amount-negative {
  color: #f56c6c;
  font-weight: bold;
}
</style>