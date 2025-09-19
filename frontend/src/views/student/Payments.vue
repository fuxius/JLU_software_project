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
          <el-radio-group v-model="paymentForm.method">
            <el-radio value="wechat">微信支付</el-radio>
            <el-radio value="alipay">支付宝</el-radio>
            <el-radio value="offline">线下支付</el-radio>
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
  balance.value = 500
}

const loadPaymentHistory = async () => {
  // TODO: 调用获取充值记录API
  paymentHistory.value = [
    {
      amount: 200,
      method: '微信支付',
      status: '已完成',
      created_at: '2024-01-10 10:30:00'
    }
  ]
}

const handlePayment = () => {
  ElMessage.success(`充值${paymentForm.amount}元成功`)
  balance.value += paymentForm.amount
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
