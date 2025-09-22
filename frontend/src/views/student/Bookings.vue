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
  // TODO: 调用获取预约列表API
  // const result = await bookingApi.getBookingList()
  // bookingList.value = result.data

  // 从localStorage读取预约记录
  const savedBookings = localStorage.getItem('student_bookings')
  if (savedBookings) {
    bookingList.value = JSON.parse(savedBookings)
  } else {
    // 默认数据
    bookingList.value = [
      {
        id: 1,
        coach_name: '张教练',
        start_time: '2024-01-15 14:00',
        end_time: '2024-01-15 15:00',
        table_number: 1,
        status: 'pending',
        total_fee: 200
      }
    ]
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

    // TODO: 调用取消预约API
    // await bookingApi.cancelBooking(booking.id)

    // 模拟API调用
    booking.status = 'cancelled'

    // 如果预约已付款，退还费用到余额
    if (booking.total_fee) {
      const currentBalance = parseInt(localStorage.getItem('student_balance') || '500')
      const newBalance = currentBalance + booking.total_fee
      localStorage.setItem('student_balance', newBalance.toString())
    }

    // 更新localStorage中的预约记录
    const existingBookings = JSON.parse(localStorage.getItem('student_bookings') || '[]')
    const updatedBookings = existingBookings.map((b: any) =>
      b.id === booking.id ? { ...b, status: 'cancelled' } : b
    )
    localStorage.setItem('student_bookings', JSON.stringify(updatedBookings))

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
