<template>
  <transition name="fade">
    <div v-if="visible" class="notification-popup">
      <div class="popup-header">
        <el-icon><BellFilled /></el-icon>
        <span>预约提醒</span>
        <el-button type="text" @click="close" class="close-btn">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
      <div class="popup-content">
        <div v-if="bookings.length === 0" class="empty">暂无即将到期的预约</div>
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
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { BellFilled, Close } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const props = defineProps<{ bookings: any[] }>()
const visible = ref(true)

const close = () => {
  visible.value = false
}

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 兼容默认导出
export default {
  name: 'NotificationPopup'
}
</script>

<style scoped>
.notification-popup {
  position: fixed;
  top: 80px;
  right: 40px;
  z-index: 9999;
  min-width: 320px;
  max-width: 400px;
  background: #fff;
  box-shadow: 0 4px 24px rgba(0,0,0,0.12);
  border-radius: 12px;
  padding: 18px 22px 12px 22px;
  animation: fadeIn 0.5s;
}
.popup-header {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
}
.popup-header .el-icon {
  margin-right: 8px;
  color: #f7ba2a;
}
.close-btn {
  margin-left: auto;
  font-size: 16px;
  color: #999;
}
.popup-content {
  margin-top: 6px;
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
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: none; }
}
</style>
