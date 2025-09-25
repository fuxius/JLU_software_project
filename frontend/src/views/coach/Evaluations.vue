<template>
  <div class="coach-evaluations">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>预约评价管理</span>
          <el-button type="primary" @click="refreshData">刷新</el-button>
        </div>
      </template>

      <!-- 统计概览 -->
      <div class="evaluation-stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic
              title="总评价数"
              :value="statistics.total_comments"
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
              :value="statistics.recent_comments ? statistics.recent_comments.length : 0"
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
          

        </el-table>
      </div>
    </el-card>


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
const statistics = reactive({
  total_comments: 0,
  average_rating: 0,
  rating_distribution: {
    "1": 0,
    "2": 0,
    "3": 0,
    "4": 0,
    "5": 0
  } as Record<string, number>,
  recent_comments: [] as any[]
})



// 方法
const formatTime = (time?: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getStudentName = (evaluation: any) => {
  return evaluation.student_name || '未知学员'
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



const loadEvaluations = async () => {
  try {
    const response = await evaluationApi.getEvaluations()
    evaluationList.value = response
  } catch (error: any) {
    console.error('加载评价列表失败:', error)
    ElMessage.error('加载评价列表失败')
  }
}

const loadPendingCourses = async () => {
  try {
    const response = await evaluationApi.getMyPendingEvaluations()
    pendingCourses.value = response.data || []
  } catch (error: any) {
    console.error('加载待评价课程失败:', error)
    ElMessage.error('加载待评价课程失败')
  }
}

const loadStatistics = async () => {
  try {
    const stats = await evaluationApi.getEvaluationStatistics()
    Object.assign(statistics, {
      total_comments: stats?.total_comments || 0,
      average_rating: stats?.average_rating || 0,
      rating_distribution: stats?.rating_distribution || {
        "1": 0, "2": 0, "3": 0, "4": 0, "5": 0
      },
      recent_comments: stats?.recent_comments || []
    })
  } catch (error: any) {
    console.error('加载统计数据失败:', error)
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