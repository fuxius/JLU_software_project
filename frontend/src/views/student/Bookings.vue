<template>
  <div class="student-bookings">
    <el-card>
      <template #header>
        <span>我的预约</span>
      </template>
      
      <el-table :data="bookingList" stripe>
        <el-table-column prop="coach_name" label="教练" />
        <el-table-column prop="start_time" label="开始时间" />
        <el-table-column prop="end_time" label="结束时间" />
        <el-table-column prop="table_number" label="球台号" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'pending'"
              type="warning" 
              size="small" 
              @click="cancelBooking(scope.row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { bookingApi } from '@/api/bookings'

const bookingList = ref([])

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待确认',
    'approved': '已确认',
    'rejected': '已拒绝',
    'cancelled': '已取消',
    'completed': '已完成'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger',
    'cancelled': 'info',
    'completed': 'success'
  }
  return typeMap[status] || 'info'
}

const loadBookingList = async () => {
  try {
    // 调用获取预约列表API
    const result = await bookingApi.getBookings()
    bookingList.value = result
  } catch (error) {
    console.error('加载预约列表失败:', error)
    ElMessage.error('加载预约列表失败')
  }
}

const cancelBooking = async (booking: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消与 ${booking.coach_name} 教练的预约吗？`,
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 调用取消预约API
    const cancelData = {
      cancellation_reason: '学员主动取消'
    }
    await bookingApi.cancelBooking(booking.id, cancelData)

    ElMessage.success(`已取消预约：${booking.coach_name}`)

    // 刷新预约列表
    await loadBookingList()
  } catch (error: any) {
    if (error === 'cancel') {
      // 用户取消操作
      return
    }
    console.error('取消预约失败:', error)
    ElMessage.error('取消预约失败，请重试')
  }
}

onMounted(() => {
  loadBookingList()
})
</script>
