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
        <el-table-column prop="coach_name" label="教练">
          <template #default="scope">
            {{ scope.row.coach_name || '未知教练' }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间">
          <template #default="scope">
            {{ scope.row.start_time || '未知时间' }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间">
          <template #default="scope">
            {{ scope.row.end_time || '未知时间' }}
          </template>
        </el-table-column>
        <el-table-column prop="table_number" label="球台号">
          <template #default="scope">
            {{ scope.row.table_number || '未知球台' }}
          </template>
        </el-table-column>
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
    <el-dialog v-model="evaluationDialogVisible" :title="dialogTitle" width="600px">
      <!-- 查看评价模式（只在存在评价且非编辑模式时显示） -->
      <div v-if="existingComment && !isEditMode">
        <el-form label-width="80px">
          <el-form-item label="评分">
            <el-rate 
              :model-value="existingComment.rating" 
              :max="5" 
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              :texts="['很差', '差', '一般', '好', '很好']"
              show-text
              disabled
            />
          </el-form-item>
          <el-form-item label="评价内容">
            <el-input
              :model-value="existingComment.content || '暂无评价内容'"
              type="textarea"
              :rows="4"
              readonly
            />
          </el-form-item>
          <el-form-item label="评价时间">
            <span>{{ formatDate(existingComment.created_at) }}</span>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 编辑/新增评价模式（在 isEditMode 为 true 或不存在 existingComment 时显示） -->
      <div v-else>
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
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 将 footer 放到 el-dialog 的直接子节点，内部用条件渲染 -->
      <template #footer>
        <div v-if="existingComment && !isEditMode">
          <el-button @click="switchToEditMode">修改评价</el-button>
          <el-button type="danger" @click="deleteComment" :loading="deletingComment">删除评价</el-button>
          <el-button @click="closeDialog">关闭</el-button>
        </div>
        <div v-else>
          <el-button @click="closeDialog">取消</el-button>
          <el-button type="primary" @click="submitEvaluation" :loading="submittingEvaluation">
            {{ isEditMode ? '更新评价' : '提交评价' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { bookingApi } from '@/api/bookings'
import { commentApi } from '@/api/comments'
import { useUserStore } from '@/store/user'

const bookingList = ref<any[]>([])

// 评价相关状态
const evaluationDialogVisible = ref(false)
const submittingEvaluation = ref(false)
const deletingComment = ref(false)
const currentBooking = ref<any>(null)
const existingComment = ref<any>(null)
const isEditMode = ref(false)
const evaluationForm = ref({
  rating: 5,
  content: ''
})

// 计算对话框标题（优先显示编辑模式）
const dialogTitle = computed(() => {
  if (isEditMode.value) {
    return '修改评价'
  } else if (existingComment.value) {
    return '查看评价'
  } else {
    return '课程评价'
  }
})

const getStatusText = (status: string) => {
  if (!status) return '未知状态'
  
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
  if (!status) return 'info'
  
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
      `确定要取消与 ${booking.coach_name || '未知教练'} 教练的预约吗？`,
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

    ElMessage.success(`已取消预约：${booking.coach_name || '未知教练'}`)

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

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 检查预约是否有评价
const checkExistingComment = async (bookingId: number) => {
  try {
    const response = await commentApi.getCommentByBooking(bookingId)
    existingComment.value = response
    return response
  } catch (error: any) {
    if (error.response?.status === 404) {
      // 没有评价是正常情况
      existingComment.value = null
      return null
    }
    console.error('检查评价失败:', error)
    ElMessage.error('检查评价失败')
    return null
  }
}

// 打开评价对话框
const evaluateBooking = async (booking: any) => {
  console.log('当前预约信息:', booking)
  console.log('当前用户角色:', useUserStore().user?.role)
  currentBooking.value = booking
  isEditMode.value = false
  evaluationForm.value = {
    rating: 5,
    content: ''
  }
  
  try {
    console.log('正在检查预约ID的评价:', booking.id)
    // 检查是否已有评价
    const comment = await checkExistingComment(booking.id)
    if (comment) {
      console.log('找到已有评价:', comment)
      existingComment.value = comment
    } else {
      console.log('未找到评价')
      existingComment.value = null
    }
    
    evaluationDialogVisible.value = true
  } catch (error: any) { // 添加类型注解
    console.error('打开评价对话框失败:', error)
    if (error.response?.status === 403) {
      ElMessage.error('权限不足：此预约可能不属于当前登录用户')
    } else {
      ElMessage.error('无法打开评价对话框')
    }
  }
}

// 切换到编辑模式
const switchToEditMode = () => {
  if (existingComment.value) {
    // 保留 existingComment（不设为 null），只切换到编辑模式并填充表单
    evaluationForm.value = {
      rating: existingComment.value.rating,
      content: existingComment.value.content || ''
    }
    isEditMode.value = true
  }
}

// 关闭对话框
const closeDialog = () => {
  evaluationDialogVisible.value = false
  existingComment.value = null
  isEditMode.value = false
  evaluationForm.value = {
    rating: 5,
    content: ''
  }
}

// 提交评价
const submitEvaluation = async () => {
  if (!currentBooking.value) {
    ElMessage.error('请选择要评价的预约')
    return
  }

  if (evaluationForm.value.rating < 1 || evaluationForm.value.rating > 5) {
    ElMessage.error('请选择1-5分的评分')
    return
  }

  try {
    submittingEvaluation.value = true

    if (isEditMode.value && existingComment.value) {
      // 更新评价
      const commentData = {
        rating: evaluationForm.value.rating,
        content: evaluationForm.value.content || undefined
      }
      await commentApi.updateComment(existingComment.value.id, commentData)
      ElMessage.success('评价更新成功！')
    } else {
      // 创建评价
      const commentData = {
        booking_id: currentBooking.value.id,
        rating: evaluationForm.value.rating,
        content: evaluationForm.value.content || undefined
      }
      await commentApi.createComment(commentData)
      ElMessage.success('评价提交成功！')
    }

    closeDialog()
    
    // 刷新预约列表
    await loadBookingList()
  } catch (error: any) {
    console.error('提交评价失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(`提交评价失败：${error.response.data.detail}`)
    } else {
      ElMessage.error('提交评价失败，请重试')
    }
  } finally {
    submittingEvaluation.value = false
  }
}

// 删除评价
const deleteComment = async () => {
  if (!existingComment.value) {
    ElMessage.error('没有可删除的评价')
    return
  }

  try {
    await ElMessageBox.confirm(
      '确定要删除这个评价吗？删除后无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    deletingComment.value = true
    await commentApi.deleteComment(existingComment.value.id)
    
    ElMessage.success('评价删除成功！')
    closeDialog()
    
    // 刷新预约列表
    await loadBookingList()
  } catch (error: any) {
    if (error === 'cancel') {
      // 用户取消操作
      return
    }
    console.error('删除评价失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(`删除评价失败：${error.response.data.detail}`)
    } else {
      ElMessage.error('删除评价失败，请重试')
    }
  } finally {
    deletingComment.value = false
  }
}

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
