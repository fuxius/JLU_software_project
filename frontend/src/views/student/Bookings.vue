<template>
  <div class="student-bookings">
    <el-card>
      <template #header>
        <div class="header-with-info">
          <span>我的预约</span>
          <el-tag v-if="getDistinctCoachesCount > 0" type="info">
            当前已预约 {{ getDistinctCoachesCount }} 个教练 (最多可预约2个不同教练)
          </el-tag>
        </div>
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
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'pending'"
              type="warning" 
              size="small" 
              @click="cancelBooking(scope.row)"
            >
              取消
            </el-button>
            <el-button 
              v-if="scope.row.status === 'confirmed'"
              type="primary" 
              size="small" 
              @click="evaluateBooking(scope.row)"
            >
              评价
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 评价对话框 -->
    <el-dialog v-model="evaluationDialogVisible" title="课程评价" width="600px">
      <el-form :model="evaluationForm" label-width="80px">
        <el-form-item label="评分">
          <el-rate 
            v-model="evaluationForm.rating" 
            :max="5" 
            :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
            :texts="['很差', '差', '一般', '好', '很好']"
            show-text
          />
        </el-form-item>
        <el-form-item label="评价内容">
          <el-input
            v-model="evaluationForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入您对本次课程的评价..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="evaluationDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEvaluation" :loading="submittingEvaluation">
          提交评价
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { bookingApi } from '@/api/bookings'

const bookingList = ref<any[]>([])

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
    const response = await bookingApi.getBookings()
    // 处理可能的响应格式（兼容数组或对象格式的返回值）
    bookingList.value = Array.isArray(response) ? response : (response.data || [])
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

// 计算已预约的不同教练数量
const getDistinctCoachesCount = computed(() => {
  // 筛选出有效预约（未取消和未拒绝）
  const validBookings = bookingList.value.filter((booking: any) => 
    booking.status !== 'cancelled' && booking.status !== 'rejected'
  )
  
  // 获取不同教练的数量
  const uniqueCoachIds = new Set(validBookings.map((booking: any) => booking.coach_id))
  return uniqueCoachIds.size
})

onMounted(() => {
  loadBookingList()
})
</script>

<style scoped>
.header-with-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
