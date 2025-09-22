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
      </div>

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
                :disabled-date="disabledDate"
                :disabled-time="disabledTime"
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
          <el-button type="primary" @click="submitBooking" :loading="submitting">
            提交预约
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { bookingApi } from '@/api/bookings'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()

const bookingFormRef = ref()
const submitting = ref(false)

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

const getLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    'senior': '高级教练',
    'intermediate': '中级教练',
    'junior': '初级教练'
  }
  return levelMap[level] || level
}

const disabledDate = (time: Date) => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  return time < today
}

const disabledTime = (time: Date) => {
  const now = new Date()
  const currentHour = now.getHours()

  return {
    disabledHours: () => {
      // 只允许9:00-21:00的整点时间
      const disabledHours = []
      for (let i = 0; i < 9; i++) {
        disabledHours.push(i)
      }
      for (let i = 22; i < 24; i++) {
        disabledHours.push(i)
      }
      return disabledHours
    },
    disabledMinutes: () => [15, 30, 45] // 只允许整点
  }
}

const submitBooking = async () => {
  if (!bookingFormRef.value) return

  try {
    await bookingFormRef.value.validate()

    // 计算预约时长和费用
    const startTime = new Date(bookingForm.start_time)
    const endTime = new Date(bookingForm.end_time)
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
})
</script>

<style scoped>
.booking-info {
  margin-bottom: 30px;
}

.coach-info {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.coach-info h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.coach-info p {
  margin: 8px 0;
  color: #606266;
}

.text-center {
  text-align: center;
}

.text-gray-500 {
  color: #909399;
}
</style>
