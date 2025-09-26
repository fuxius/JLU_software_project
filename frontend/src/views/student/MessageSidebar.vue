<template>
  <div class="message-sidebar">
    <div class="sidebar-header">
      <el-icon><BellFilled /></el-icon>
      <span>消息</span>
    </div>
    <div class="sidebar-content">
      <div v-if="bookings.length === 0" class="empty">暂无24小时内的预约提醒</div>
      <div v-for="booking in bookings" :key="booking.id" class="booking-item">
        <el-tag type="warning" class="tag">即将开始</el-tag>
        <div class="info">
          <div><b>时间：</b>{{ formatDate(booking.start_time) }}</div>
          <div><b>场地：</b>{{ booking.court_name || booking.court || '未知' }}</div>
          <div><b>教练：</b>{{ booking.coach_name || booking.coach || '无' }}</div>
          <div><b>预约类型：</b>{{ booking.type || '普通预约' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { BellFilled } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const bookings = ref<any[]>([])

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const fetchBookings = async () => {
  try {
    const res = await fetch('/api/v1/student/bookings')
    const data = await res.json()
    const now = dayjs()
    bookings.value = (data.items || data.data || data || []).filter((b: any) => {
      if (!b.start_time) return false
      const diff = dayjs(b.start_time).diff(now, 'hour')
      return diff >= 0 && diff < 24
    })
  } catch (e) {
    bookings.value = []
  }
}

onMounted(() => {
  fetchBookings()
})
</script>

<style scoped>
.message-sidebar {
  position: fixed;
  top: 80px;
  right: 0;
  width: 340px;
  height: 70vh;
  background: #fff;
  box-shadow: -2px 0 16px rgba(0,0,0,0.08);
  border-radius: 12px 0 0 12px;
  padding: 18px 18px 12px 18px;
  z-index: 999;
  display: flex;
  flex-direction: column;
}
.sidebar-header {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
}
.sidebar-header .el-icon {
  margin-right: 8px;
  color: #f7ba2a;
}
.sidebar-content {
  flex: 1;
  overflow-y: auto;
}
.booking-item {
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  display: flex;
  align-items: flex-start;
}
.booking-item .tag {
  margin-right: 10px;
}
.booking-item .info {
  flex: 1;
  font-size: 15px;
  color: #333;
}
.empty {
  color: #aaa;
  text-align: center;
  padding: 16px 0;
}
</style>
