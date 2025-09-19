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
import { ElMessage } from 'element-plus'

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
  bookingList.value = [
    {
      id: 1,
      coach_name: '张教练',
      start_time: '2024-01-15 14:00',
      end_time: '2024-01-15 15:00',
      table_number: 1,
      status: 'pending'
    }
  ]
}

const cancelBooking = (booking: any) => {
  ElMessage.success(`已取消预约：${booking.coach_name}`)
}

onMounted(() => {
  loadBookingList()
})
</script>
