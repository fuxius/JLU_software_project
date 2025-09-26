<template>
  <div class="messages-page">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <el-icon><BellFilled /></el-icon>
          <span>消息中心</span>
        </div>
      </template>

      <div class="messages-content">
        <div v-if="loading" class="loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        
        <div v-else-if="upcomingBookings.length === 0" class="empty">
          <el-empty description="暂无24小时内的预约提醒" />
        </div>
        
        <div v-else>
          <h3 class="section-title">即将到期的预约提醒</h3>
          <div v-for="booking in upcomingBookings" :key="booking.id" class="booking-card">
            <el-card shadow="hover">
              <div class="booking-header">
                <el-tag type="warning">即将开始</el-tag>
                <span class="time-remaining">{{ getTimeRemaining(booking.start_time) }}</span>
              </div>
              <div class="booking-info">
                <div class="info-row">
                  <el-icon><Clock /></el-icon>
                  <span><b>预约时间：</b>{{ formatDateTime(booking.start_time) }}</span>
                </div>
                <div class="info-row">
                  <el-icon><Location /></el-icon>
                  <span><b>球台号：</b>{{ booking.table_number || '未安排' }}</span>
                </div>
                <div class="info-row">
                  <el-icon><UserFilled /></el-icon>
                  <span><b>预约教练：</b>{{ booking.coach_name || '教练ID: ' + booking.coach_id }}</span>
                </div>
                <div class="info-row">
                  <el-icon><Document /></el-icon>
                  <span><b>预约状态：</b>{{ getStatusText(booking.status) }}</span>
                </div>
              </div>
            </el-card>
          </div>
        </div>

        <div class="refresh-section">
          <el-button type="primary" @click="refreshMessages" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新消息
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { BellFilled, Clock, Location, UserFilled, Document, Loading, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { bookingApi } from '../../api/bookings'
import dayjs from 'dayjs'

const loading = ref(false)
const upcomingBookings = ref<any[]>([])

const formatDateTime = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getTimeRemaining = (date: string) => {
  const now = dayjs()
  const target = dayjs(date)
  const hours = target.diff(now, 'hour')
  const minutes = target.diff(now, 'minute') % 60
  
  if (hours > 0) {
    return `还有 ${hours} 小时 ${minutes} 分钟`
  } else {
    return `还有 ${minutes} 分钟`
  }
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待确认',
    'confirmed': '已确认',
    'approved': '已同意',
    'rejected': '已拒绝',
    'cancelled': '已取消',
    'completed': '已完成'
  }
  return statusMap[status] || status
}

const fetchBookings = async () => {
  try {
    loading.value = true
    const response = await bookingApi.getBookings()
    const bookings = Array.isArray(response.data) ? response.data : (response as any)
    const now = dayjs()
    upcomingBookings.value = bookings.filter((b: any) => {
      if (!b.start_time) return false
      const diff = dayjs(b.start_time).diff(now, 'hour')
      return diff >= 0 && diff < 24
    })
  } catch (e) {
    console.error('获取预约信息失败:', e)
    ElMessage.error('获取预约信息失败')
    upcomingBookings.value = []
  } finally {
    loading.value = false
  }
}

const refreshMessages = () => {
  fetchBookings()
}

onMounted(() => {
  fetchBookings()
})
</script>

<style scoped>
.messages-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
}

.card-header .el-icon {
  margin-right: 8px;
  color: #f7ba2a;
}

.messages-content {
  min-height: 400px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #999;
}

.loading .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.section-title {
  margin-bottom: 20px;
  color: #333;
  font-size: 16px;
}

.booking-card {
  margin-bottom: 16px;
}

.booking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.time-remaining {
  color: #f7ba2a;
  font-weight: 600;
}

.booking-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-row .el-icon {
  color: #409eff;
  width: 16px;
}

.refresh-section {
  margin-top: 30px;
  text-align: center;
}
</style>