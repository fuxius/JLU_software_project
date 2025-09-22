<template>
  <div class="coach-bookings">
    <el-card>
      <template #header>
        <span>课程安排</span>
      </template>
      
      <el-table :data="bookingList" stripe>
        <el-table-column prop="student_name" label="学员" />
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
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'pending'"
              type="success" 
              size="small" 
              @click="approveBooking(scope.row)"
            >
              确认
            </el-button>
            <el-button 
              v-if="scope.row.status === 'pending'"
              type="danger" 
              size="small" 
              @click="rejectBooking(scope.row)"
            >
              拒绝
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
    'confirmed': '已确认',
    'rejected': '已拒绝',
    'cancelled': '已取消',
    'completed': '已完成'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    'pending': 'warning',
    'confirmed': 'success',
    'rejected': 'danger',
    'cancelled': 'info',
    'completed': 'success'
  }
  return typeMap[status] || 'info'
}

const loadBookingList = async () => {
  try {
    // 获取教练的所有预约
    const bookings = await bookingApi.getBookings()
    bookingList.value = bookings
  } catch (error) {
    console.error('加载预约列表失败:', error)
    ElMessage.error('加载预约列表失败')
    
    // 如果API失败，使用静态数据作为后备
    bookingList.value = [
      {
        id: 1,
        student_name: '小明',
        start_time: '2024-01-15 14:00',
        end_time: '2024-01-15 15:00',
        table_number: 1,
        status: 'pending'
      }
    ]
  }
}

const approveBooking = async (booking: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要确认学员 ${booking.student_name} 的预约吗？`,
      '确认预约',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await bookingApi.confirmBooking(booking.id, { action: 'confirm' })
    ElMessage.success(`已确认预约：${booking.student_name}`)
    await loadBookingList() // 重新加载列表
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('确认预约失败:', error)
      ElMessage.error('确认预约失败')
    }
  }
}

const rejectBooking = async (booking: any) => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      `请输入拒绝 ${booking.student_name} 预约的原因：`,
      '拒绝预约',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入拒绝原因'
      }
    )
    
    await bookingApi.confirmBooking(booking.id, { 
      action: 'reject', 
      message: reason 
    })
    ElMessage.success(`已拒绝预约：${booking.student_name}`)
    await loadBookingList() // 重新加载列表
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('拒绝预约失败:', error)
      ElMessage.error('拒绝预约失败')
    }
  }
}

onMounted(() => {
  loadBookingList()
})
</script>
