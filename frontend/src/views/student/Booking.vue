<template>
  <div class="booking-page">
    <el-card>
      <template #header>
        <span>预约教练</span>
      </template>

      <div class="booking-info">
        <div class="coach-info">
          <h3>教练信息</h3>
          <p><strong>教练姓名：</strong>{{ selectedCoach.name }}</p>
          <p><strong>等级：</strong>{{ getLevelText(selectedCoach.level) }}</p>
          <p><strong>收费标准：</strong>{{ selectedCoach.hourly_rate }}元/小时</p>
        </div>
        
        <div class="balance-info">
          <h3>账户信息</h3>
          <p><strong>当前余额：</strong><span class="balance">￥{{ currentBalance }}</span></p>
          <p v-if="bookingTotalFee > 0"><strong>预约费用：</strong><span class="total-fee">￥{{ bookingTotalFee }}</span></p>
          <p v-if="bookingDuration > 0"><strong>预约时长：</strong>{{ bookingDuration }}小时</p>
        </div>
      </div>

      <!-- 余额不足警告 -->
      <el-alert
        v-if="balanceWarningMessage"
        :title="balanceWarningMessage"
        type="warning"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #default>
          <div>
            {{ balanceWarningMessage }}
            <el-button 
              type="text" 
              size="small" 
              @click="router.push('/student/payments')"
              style="margin-left: 10px;"
            >
              立即充值
            </el-button>
          </div>
        </template>
      </el-alert>

      <el-form :model="bookingForm" :rules="bookingRules" ref="bookingFormRef" label-width="100px">
        <el-form-item label="预约时间" required>
          <el-col :span="11">
            <el-form-item prop="start_time">
              <el-date-picker
                v-model="bookingForm.start_time"
                type="datetime"
                placeholder="选择开始时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
                :disabled-date="disabledDate"
                :disabled-time="disabledTime"
              />
            </el-form-item>
          </el-col>
          <el-col :span="2" class="text-center">
            <span class="text-gray-500">至</span>
          </el-col>
          <el-col :span="11">
            <el-form-item prop="end_time">
              <el-date-picker
                v-model="bookingForm.end_time"
                type="datetime"
                placeholder="选择结束时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
                :disabled-date="disabledEndDate"
                :disabled-time="disabledEndTime"
              />
            </el-form-item>
          </el-col>
        </el-form-item>

        <el-form-item label="球台号" prop="table_number">
          <el-select v-model="bookingForm.table_number" placeholder="请选择球台">
            <el-option
              v-for="i in 10"
              :key="i"
              :label="`球台${i}`"
              :value="i"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="bookingForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入预约备注（可选）"
          />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="submitBooking" 
            :loading="submitting"
            :disabled="!isBalanceSufficient || submitting"
          >
            提交预约
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { bookingApi } from '@/api/bookings'
import { paymentApi } from '@/api/payments'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()

const bookingFormRef = ref()
const submitting = ref(false)
const currentBalance = ref(0) // 添加余额状态

const selectedCoach = ref({
  id: 0,
  name: '',
  level: '',
  hourly_rate: 0
})

const bookingForm = reactive({
  start_time: '',
  end_time: '',
  table_number: null as number | null,
  notes: ''
})

const bookingRules = {
  start_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  end_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ],
  table_number: [
    { required: true, message: '请选择球台号', trigger: 'change' }
  ]
}

// 计算预约时长（小时）
const bookingDuration = computed(() => {
  if (!bookingForm.start_time || !bookingForm.end_time) return 0
  const startTime = new Date(bookingForm.start_time)
  const endTime = new Date(bookingForm.end_time)
  const duration = (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60)
  return duration > 0 ? duration : 0
})

// 计算预约总费用
const bookingTotalFee = computed(() => {
  return Math.round(bookingDuration.value * selectedCoach.value.hourly_rate)
})

// 检查余额是否足够
const isBalanceSufficient = computed(() => {
  return currentBalance.value >= bookingTotalFee.value
})

// 余额不足提示信息
const balanceWarningMessage = computed(() => {
  if (bookingTotalFee.value > 0 && !isBalanceSufficient.value) {
    const shortage = bookingTotalFee.value - currentBalance.value
    return `余额不足！当前余额：￥${currentBalance.value}，预约费用：￥${bookingTotalFee.value}，还需充值：￥${shortage}`
  }
  return ''
})

const getLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    'senior': '高级教练',
    'intermediate': '中级教练',
    'junior': '初级教练'
  }
  return levelMap[level] || level
}

// 加载用户余额
const loadUserBalance = async () => {
  try {
    const response: any = await paymentApi.getBalance()
    // 处理可能的响应格式
    const balance = response?.data?.balance ?? response?.balance ?? 0
    currentBalance.value = balance
  } catch (error) {
    console.error('加载余额失败:', error)
    ElMessage.error('加载余额失败')
    // 如果API失败，设为0确保安全
    currentBalance.value = 0
  }
}

const disabledDate = (time: Date) => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  return time < today
}

const disabledTime = (time: Date, role?: string) => {
  const now = new Date()
  const selectedDate = new Date(time.getFullYear(), time.getMonth(), time.getDate())
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const isToday = selectedDate.getTime() === today.getTime()

  return {
    disabledHours: () => {
      const disabledHours = []
      
      // 只允许9:00-21:00的整点时间
      for (let i = 0; i < 9; i++) {
        disabledHours.push(i)
      }
      for (let i = 22; i < 24; i++) {
        disabledHours.push(i)
      }
      
      // 如果是今天，还要禁用已经过去的小时
      if (isToday) {
        const currentHour = now.getHours()
        for (let i = 9; i <= currentHour; i++) {
          if (i < 22) {  // 只在营业时间范围内添加
            disabledHours.push(i)
          }
        }
      }
      
      return disabledHours
    },
    disabledMinutes: (hour: number) => {
      const disabledMinutes = [15, 30, 45] // 只允许整点
      
      // 如果是今天的当前小时，还要禁用已经过去的分钟
      if (isToday && hour === now.getHours()) {
        const currentMinute = now.getMinutes()
        // 如果当前时间已经过了整点，就禁用0分钟
        if (currentMinute > 0) {
          disabledMinutes.push(0)
        }
      }
      
      return disabledMinutes
    }
  }
}

// 结束时间的日期限制
const disabledEndDate = (time: Date) => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const selectedDate = new Date(time.getFullYear(), time.getMonth(), time.getDate())
  
  // 不能选择今天之前的日期
  if (selectedDate < today) {
    return true
  }
  
  // 如果有开始时间，结束日期不能早于开始日期
  if (bookingForm.start_time) {
    const startDate = new Date(bookingForm.start_time)
    const startDateOnly = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate())
    return selectedDate < startDateOnly
  }
  
  return false
}

// 结束时间的时间限制
const disabledEndTime = (time: Date) => {
  const now = new Date()
  const selectedDate = new Date(time.getFullYear(), time.getMonth(), time.getDate())
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const isToday = selectedDate.getTime() === today.getTime()

  return {
    disabledHours: () => {
      const disabledHours = []
      
      // 只允许9:00-21:00的整点时间
      for (let i = 0; i < 9; i++) {
        disabledHours.push(i)
      }
      for (let i = 22; i < 24; i++) {
        disabledHours.push(i)
      }
      
      // 如果是今天，还要禁用已经过去的小时
      if (isToday) {
        const currentHour = now.getHours()
        for (let i = 9; i <= currentHour; i++) {
          if (i < 22) {
            disabledHours.push(i)
          }
        }
      }
      
      // 如果有开始时间，结束时间不能早于或等于开始时间
      if (bookingForm.start_time) {
        const startTime = new Date(bookingForm.start_time)
        const startDate = new Date(startTime.getFullYear(), startTime.getMonth(), startTime.getDate())
        
        // 如果是同一天
        if (selectedDate.getTime() === startDate.getTime()) {
          const startHour = startTime.getHours()
          for (let i = 9; i <= startHour; i++) {
            if (i < 22) {
              disabledHours.push(i)
            }
          }
        }
      }
      
      return [...new Set(disabledHours)] // 去重
    },
    disabledMinutes: (hour: number) => {
      const disabledMinutes = [15, 30, 45] // 只允许整点
      
      // 如果是今天的当前小时，还要禁用已经过去的分钟
      if (isToday && hour === now.getHours()) {
        const currentMinute = now.getMinutes()
        if (currentMinute > 0) {
          disabledMinutes.push(0)
        }
      }
      
      // 如果有开始时间，且选择的是开始时间的同一小时，禁用0分钟
      if (bookingForm.start_time) {
        const startTime = new Date(bookingForm.start_time)
        const startDate = new Date(startTime.getFullYear(), startTime.getMonth(), startTime.getDate())
        
        if (selectedDate.getTime() === startDate.getTime() && hour === startTime.getHours()) {
          disabledMinutes.push(0)
        }
      }
      
      return disabledMinutes
    }
  }
}

const submitBooking = async () => {
  if (!bookingFormRef.value) return

  try {
    await bookingFormRef.value.validate()

    // 计算预约时长和费用
    const startTime = new Date(bookingForm.start_time)
    const endTime = new Date(bookingForm.end_time)
    const now = new Date()

    // 检查开始时间是否早于当前时间
    if (startTime <= now) {
      ElMessage.error('预约开始时间不能早于或等于当前时间')
      return
    }

    // 检查结束时间是否早于当前时间
    if (endTime <= now) {
      ElMessage.error('预约结束时间不能早于或等于当前时间')
      return
    }

    const duration = (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60) // 小时

    if (duration <= 0) {
      ElMessage.error('结束时间必须晚于开始时间')
      return
    }

    if (duration > 3) {
      ElMessage.error('单次预约不能超过3小时')
      return
    }

    const totalFee = Math.round(duration * selectedCoach.value.hourly_rate)

    // 检查余额是否充足
    if (currentBalance.value < totalFee) {
      const shortage = totalFee - currentBalance.value
      ElMessage.error(`余额不足！当前余额：￥${currentBalance.value}，预约费用：￥${totalFee}，还需充值：￥${shortage}`)
      return
    }

    submitting.value = true

    try {
      // 获取当前用户信息
      const userStore = useUserStore()
      if (!userStore.user) {
        ElMessage.error('用户信息不完整，请重新登录')
        return
      }

      // 调用预约API
      const bookingData = {
        coach_id: selectedCoach.value.id,
        student_id: userStore.user.id, // 添加student_id
        campus_id: userStore.user.campus_id || 1, // 如果没有campus_id，默认使用主校区
        start_time: bookingForm.start_time,
        end_time: bookingForm.end_time,
        duration_hours: duration,
        booking_message: bookingForm.notes,
        table_number: bookingForm.table_number?.toString()
      }

      const result = await bookingApi.createBooking(bookingData)

      ElMessage.success(`预约成功！费用：${totalFee}元，预约时长：${duration}小时`)

      router.push('/student/bookings')
    } catch (error: any) {
      console.error('预约失败:', error)
      if (error.response?.status === 403) {
        ElMessage.error('权限不足或参数错误，请检查用户信息和教练信息')
      } else {
        ElMessage.error(error.message || '预约失败，请重试')
      }
    } finally {
      submitting.value = false
    }
  } catch (error: any) {
    if (error !== 'validation failed') {
      console.error('预约失败:', error)
      ElMessage.error('预约失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/student/coaches')
}

onMounted(() => {
  // 从路由参数获取教练信息
  if (route.query.coachId && route.query.coachName && route.query.hourlyRate) {
    selectedCoach.value = {
      id: parseInt(route.query.coachId as string),
      name: route.query.coachName as string,
      level: 'intermediate', // 默认值
      hourly_rate: parseInt(route.query.hourlyRate as string)
    }
  } else {
    ElMessage.error('未选择教练，请重新选择')
    router.push('/student/coaches')
  }

  // 加载用户余额
  loadUserBalance()
})
</script>

<style scoped>
.booking-info {
  margin-bottom: 30px;
  display: flex;
  gap: 20px;
}

.coach-info, .balance-info {
  flex: 1;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.coach-info h3, .balance-info h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.coach-info p, .balance-info p {
  margin: 8px 0;
  color: #606266;
}

.balance {
  color: #67c23a;
  font-weight: bold;
}

.total-fee {
  color: #409eff;
  font-weight: bold;
}

.text-center {
  text-align: center;
}

.text-gray-500 {
  color: #909399;
}

@media (max-width: 768px) {
  .booking-info {
    flex-direction: column;
  }
}
</style>
