<template>
  <div class="coach-evaluations">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课后评价管理</span>
          <el-button type="primary" @click="refreshData">刷新</el-button>
        </div>
      </template>

      <!-- 统计概览 -->
      <div class="evaluation-stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic
              title="总评价数"
              :value="statistics.total_evaluations"
              suffix="条"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="平均评分"
              :value="statistics.average_rating"
              :precision="1"
              suffix="分"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="本月评价"
              :value="statistics.recent_evaluations"
              suffix="条"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="待评价课程"
              :value="pendingCourses.length"
              suffix="个"
            />
          </el-col>
        </el-row>
      </div>

      <!-- 待评价课程 -->
      <div v-if="pendingCourses.length > 0" class="pending-evaluations">
        <el-divider content-position="left">待评价课程</el-divider>
        <el-row :gutter="20">
          <el-col 
            v-for="course in pendingCourses" 
            :key="course.course_id" 
            :span="8"
            class="mb-20"
          >
            <el-card shadow="hover" class="pending-course-card">
              <div class="course-info">
                <h4>与 {{ course.booking.student_name }} 的课程</h4>
                <p>上课时间：{{ formatTime(course.booking.start_time) }}</p>
                <p>完成时间：{{ formatTime(course.completed_at) }}</p>
              </div>
              <div class="course-actions">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="openEvaluationDialog(course)"
                >
                  评价课程
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 评价列表 -->
      <div class="evaluations-list">
        <el-divider content-position="left">历史评价</el-divider>
        
        <el-table :data="evaluationList" stripe>
          <el-table-column label="课程信息" width="200">
            <template #default="scope">
              <div>
                <p><strong>学员：</strong>{{ getStudentName(scope.row) }}</p>
                <p><strong>时间：</strong>{{ formatTime(scope.row.created_at) }}</p>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="评分" width="100">
            <template #default="scope">
              <el-rate 
                v-model="scope.row.rating" 
                disabled 
                show-score
                score-template="{value} 分"
              />
            </template>
          </el-table-column>
          
          <el-table-column label="评价内容" min-width="300">
            <template #default="scope">
              <div class="evaluation-content">
                {{ scope.row.content }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row)">
                {{ getStatusText(scope.row) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button 
                v-if="canEdit(scope.row)"
                type="primary" 
                size="small"
                @click="editEvaluation(scope.row)"
              >
                编辑
              </el-button>
              <el-button 
                type="danger" 
                size="small"
                @click="deleteEvaluation(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 评价对话框 -->
    <el-dialog
      v-model="evaluationDialogVisible"
      :title="isEditing ? '编辑评价' : '课程评价'"
      width="600px"
    >
      <el-form
        ref="evaluationFormRef"
        :model="evaluationForm"
        :rules="evaluationRules"
        label-width="80px"
      >
        <el-form-item label="评分" prop="rating">
          <el-rate 
            v-model="evaluationForm.rating" 
            show-text
            :texts="['非常不满意', '不满意', '一般', '满意', '非常满意']"
          />
        </el-form-item>
        
        <el-form-item label="评价内容" prop="content">
          <el-input
            v-model="evaluationForm.content"
            type="textarea"
            :rows="5"
            placeholder="请输入对本次课程的评价..."
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="evaluationDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            :loading="submitting"
            @click="submitEvaluation"
          >
            {{ isEditing ? '更新' : '提交' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { evaluationApi } from '@/api/evaluations'
import type { 
  EvaluationResponse, 
  PendingEvaluationCourse, 
  EvaluationSummary,
  EvaluationCreate,
  EvaluationUpdate
} from '@/api/evaluations'

// 响应式数据
const evaluationList = ref<EvaluationResponse[]>([])
const pendingCourses = ref<PendingEvaluationCourse[]>([])
const statistics = ref<EvaluationSummary>({
  total_evaluations: 0,
  average_rating: 0,
  rating_distribution: {},
  recent_evaluations: 0
})

const evaluationDialogVisible = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const currentCourse = ref<PendingEvaluationCourse | null>(null)
const currentEvaluation = ref<EvaluationResponse | null>(null)

// 表单数据
const evaluationForm = reactive({
  course_id: 0,
  rating: 5,
  content: ''
})

const evaluationRules = {
  content: [
    { required: true, message: '请输入评价内容', trigger: 'blur' },
    { min: 1, max: 2000, message: '评价内容长度在 1 到 2000 个字符', trigger: 'blur' }
  ]
}

// 方法
const formatTime = (time?: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getStudentName = (evaluation: EvaluationResponse) => {
  // 这里需要从课程信息中获取学员姓名
  // 实际项目中应该在API返回中包含相关信息
  return '学员姓名' // 占位符
}

const getStatusType = (evaluation: EvaluationResponse) => {
  if (evaluation.updated_at && evaluation.updated_at !== evaluation.created_at) {
    return 'warning'
  }
  return 'success'
}

const getStatusText = (evaluation: EvaluationResponse) => {
  if (evaluation.updated_at && evaluation.updated_at !== evaluation.created_at) {
    return '已修改'
  }
  return '原始评价'
}

const canEdit = (evaluation: EvaluationResponse) => {
  return evaluationApi.canEditEvaluation(evaluation.created_at)
}

const openEvaluationDialog = (course: PendingEvaluationCourse) => {
  currentCourse.value = course
  isEditing.value = false
  evaluationForm.course_id = course.course_id
  evaluationForm.rating = 5
  evaluationForm.content = ''
  evaluationDialogVisible.value = true
}

const editEvaluation = (evaluation: EvaluationResponse) => {
  currentEvaluation.value = evaluation
  isEditing.value = true
  evaluationForm.course_id = evaluation.course_id
  evaluationForm.rating = evaluation.rating || 5
  evaluationForm.content = evaluation.content
  evaluationDialogVisible.value = true
}

const submitEvaluation = async () => {
  submitting.value = true
  
  try {
    if (isEditing.value && currentEvaluation.value) {
      // 更新评价
      const updateData: EvaluationUpdate = {
        content: evaluationForm.content,
        rating: evaluationForm.rating
      }
      await evaluationApi.updateEvaluation(currentEvaluation.value.id, updateData)
      ElMessage.success('评价更新成功')
    } else {
      // 创建评价
      const createData: EvaluationCreate = {
        course_id: evaluationForm.course_id,
        content: evaluationForm.content,
        rating: evaluationForm.rating
      }
      await evaluationApi.createEvaluation(createData)
      ElMessage.success('评价提交成功')
    }
    
    evaluationDialogVisible.value = false
    await refreshData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const deleteEvaluation = async (evaluation: EvaluationResponse) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评价吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await evaluationApi.deleteEvaluation(evaluation.id)
    ElMessage.success('评价删除成功')
    await refreshData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const loadEvaluations = async () => {
  try {
    const response = await evaluationApi.getEvaluations({
      evaluator_type: 'coach'
    })
    evaluationList.value = response
  } catch (error: any) {
    ElMessage.error('加载评价列表失败')
  }
}

const loadPendingCourses = async () => {
  try {
    const response = await evaluationApi.getMyPendingEvaluations()
    pendingCourses.value = response
  } catch (error: any) {
    ElMessage.error('加载待评价课程失败')
  }
}

const loadStatistics = async () => {
  try {
    const response = await evaluationApi.getEvaluationStatistics()
    statistics.value = response
  } catch (error: any) {
    ElMessage.error('加载统计数据失败')
  }
}

const refreshData = async () => {
  await Promise.all([
    loadEvaluations(),
    loadPendingCourses(),
    loadStatistics()
  ])
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.coach-evaluations {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.evaluation-stats {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.pending-evaluations {
  margin-bottom: 30px;
}

.pending-course-card {
  height: 100%;
}

.course-info {
  margin-bottom: 15px;
}

.course-info h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.course-info p {
  margin: 5px 0;
  color: #606266;
  font-size: 14px;
}

.course-actions {
  text-align: center;
}

.evaluation-content {
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mb-20 {
  margin-bottom: 20px;
}
</style>