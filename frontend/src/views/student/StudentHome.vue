<template>
  <div>
    <!-- 其他内容 ... -->
    <NotificationPopup v-if="showNotification" :bookings="upcomingBookings" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import NotificationPopup from './NotificationPopup.vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const showNotification = ref(false)
const upcomingBookings = ref<any[]>([])

// 获取预约列表
const fetchBookings = async () => {
  try {
    const res = await fetch('/student/bookings')
    const data = await res.json()
    // 只筛选24小时内的预约
    const now = dayjs()
    upcomingBookings.value = (data.items || data.data || data || []).filter((b: any) => {
      if (!b.start_time) return false
      const diff = dayjs(b.start_time).diff(now, 'hour')
      return diff >= 0 && diff < 24
    })
    showNotification.value = upcomingBookings.value.length > 0
  } catch (e) {
    ElMessage.error('获取预约信息失败')
  }
}

onMounted(() => {
  fetchBookings()
})
</script>
