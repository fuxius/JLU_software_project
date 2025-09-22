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
            <el-radio value="wechat" label="微信支付">微信支付</el-radio>
            <el-radio value="alipay" label="支付宝">支付宝</el-radio>
            <el-radio value="offline" label="线下支付">线下支付</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handlePayment">充值</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>充值记录</span>
      </template>
      
      <el-table :data="paymentHistory" stripe>
        <el-table-column prop="amount" label="金额" />
        <el-table-column prop="method" label="支付方式" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="created_at" label="时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const balance = ref(0)
const paymentForm = reactive({
  amount: 100,
  method: 'wechat'
})
const paymentHistory = ref([])

const loadBalance = async () => {
  // TODO: 调用获取余额API
  // const result = await paymentApi.getBalance()
  // balance.value = result.data.balance

  // 从localStorage读取余额
  const savedBalance = localStorage.getItem('student_balance')
  balance.value = savedBalance ? parseInt(savedBalance) : 500
}

const loadPaymentHistory = async () => {
  // TODO: 调用获取充值记录API
  // const result = await paymentApi.getPaymentHistory()
  // paymentHistory.value = result.data

  // 从localStorage读取充值记录
  const savedHistory = localStorage.getItem('student_payment_history')
  if (savedHistory) {
    paymentHistory.value = JSON.parse(savedHistory)
  } else {
    // 默认充值记录
    paymentHistory.value = [
      {
        amount: 200,
        method: '微信支付',
        status: '已完成',
        created_at: '2024-01-10 10:30:00'
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
    // TODO: 调用实际的充值API
    // const result = await paymentApi.recharge({
    //   amount: paymentForm.amount,
    //   method: paymentForm.method
    // })

    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))

    // 创建充值记录
    const paymentRecord = {
      amount: paymentForm.amount,
      method: paymentForm.method === 'wechat' ? '微信支付' :
              paymentForm.method === 'alipay' ? '支付宝' : '线下支付',
      status: '已完成',
      created_at: new Date().toLocaleString()
    }

    // 保存充值记录到localStorage
    const existingHistory = JSON.parse(localStorage.getItem('student_payment_history') || '[]')
    existingHistory.unshift(paymentRecord)
    localStorage.setItem('student_payment_history', JSON.stringify(existingHistory))

    // 更新余额
    const currentBalance = parseInt(localStorage.getItem('student_balance') || '500')
    const newBalance = currentBalance + paymentForm.amount
    localStorage.setItem('student_balance', newBalance.toString())
    balance.value = newBalance

    ElMessage.success(`充值${paymentForm.amount}元成功`)

    // 刷新充值记录
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
</style>
