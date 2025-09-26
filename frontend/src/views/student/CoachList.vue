<template>
  <div class="coach-list">
    <el-card>
      <template #header>
        <span>教练列表</span>
      </template>
      
      <div class="search-bar">
        <el-form :model="searchForm" inline>
          <el-form-item label="教练姓名">
            <el-input v-model="searchForm.name" placeholder="请输入教练姓名" clearable />
          </el-form-item>
          <el-form-item label="性别">
            <el-select v-model="searchForm.gender" placeholder="请选择性别" clearable>
              <el-option label="男" value="male" />
              <el-option label="女" value="female" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div class="coach-grid">
        <div v-for="coach in coachList" :key="coach.id" class="coach-card">
          <el-card shadow="hover">
            <div class="coach-info">
              <div class="coach-avatar">
                <el-avatar :size="80" :src="coach.avatar" />
              </div>
              <div class="coach-details">
                <h3>{{ coach.user?.real_name || '教练' }}</h3>
                <p><el-tag :type="getLevelTagType(coach.level)">{{ getLevelText(coach.level) }}</el-tag></p>
                <p>收费：{{ coach.hourly_rate }}元/小时</p>
                <p>性别：{{ (coach.user?.gender || 'male') === 'male' ? '男' : '女' }}</p>
                <p>年龄：{{ coach.user?.age ?? '-' }}岁</p>
              </div>
            </div>
            <div class="coach-actions">
              <el-button type="primary" @click="selectCoach(coach)">选择教练</el-button>
              <el-button @click="openCoachDetail(coach)">查看详情</el-button>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="detailVisible" title="教练详情" width="720px">
      <div v-if="currentCoach" class="coach-detail-content">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h3>基本信息</h3>
          <p>姓名：{{ currentCoach.user?.real_name || '-' }}</p>
          <p>级别：{{ getLevelText(currentCoach.level) }}</p>
          <p>收费：{{ currentCoach.hourly_rate }} 元/小时</p>
          <p>性别：{{ (currentCoach.user?.gender || 'male') === 'male' ? '男' : '女' }}</p>
          <p>年龄：{{ currentCoach.user?.age ?? '-' }}</p>
          <p>简介：{{ currentCoach.achievements || '暂无' }}</p>
        </div>
        
        <!-- 评分统计 -->
        <div v-if="coachStats" class="detail-section">
          <h3>评分统计</h3>
          <div class="rating-stats">
            <div class="average-rating">
              <span class="rating-number">{{ coachStats.average_rating.toFixed(1) }}</span>
              <el-rate
                :model-value="coachStats.average_rating"
                disabled
                show-score
                :max="5"
                :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              />
              <span class="total-comments">({{ coachStats.total_comments }}条评价)</span>
            </div>
            <div class="rating-distribution">
              <div v-for="i in 5" :key="i" class="rating-bar">
                <span class="rating-label">{{ i }}星</span>
                <el-progress
                  :percentage="((coachStats.rating_distribution[i] || 0) / coachStats.total_comments * 100) || 0"
                  :format="(p: number) => coachStats.rating_distribution[i] || 0 + '条'"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 最近评价 -->
        <div v-if="coachStats?.recent_comments?.length" class="detail-section">
          <h3>最近评价</h3>
          <el-timeline>
            <el-timeline-item
              v-for="comment in coachStats.recent_comments"
              :key="comment.id"
              :timestamp="formatDate(comment.created_at)"
              placement="top"
            >
              <div class="comment-item">
                <el-rate
                  :model-value="comment.rating"
                  disabled
                  :max="5"
                  :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                />
                <div class="comment-content">
                  {{ comment.content || '未留下评价内容' }}
                </div>
                <div class="comment-info">
                  <span>{{ formatDate(comment.booking_start_time) }}</span>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
        
        <div v-else-if="coachStats" class="detail-section">
          <el-empty description="暂无评价" />
        </div>

        <div v-if="loading" class="loading-section">
          <el-skeleton :rows="3" animated />
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button type="primary" @click="selectCoach(currentCoach)">选择教练</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { coachApi } from '@/api/coaches'
import { bookingApi } from '@/api/bookings'
import { commentApi } from '@/api/comments'
import { useUserStore } from '@/store/user'
import type { CoachCommentStats } from '@/api/comments'

const router = useRouter()

const searchForm = reactive({
  name: '',
  gender: ''
})

const allCoaches = ref<any[]>([])  // 存储所有教练数据
const detailVisible = ref(false)
const currentCoach = ref<any | null>(null)
const coachStats = ref<CoachCommentStats | null>(null)
const loading = ref(false)

// 格式化日期
const formatDate = (dateString: string | undefined) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 计算属性：根据搜索条件过滤教练列表
const coachList = computed(() => {
  let filtered = allCoaches.value

  // 按姓名搜索
  if (searchForm.name.trim()) {
    const searchName = searchForm.name.toLowerCase()
    filtered = filtered.filter(coach => {
      const realName = coach.user?.real_name?.toLowerCase() || ''
      const name = coach.name?.toLowerCase() || ''
      return realName.includes(searchName) || name.includes(searchName)
    })
  }

  // 按性别筛选
  if (searchForm.gender) {
    filtered = filtered.filter(coach => {
      const gender = coach.user?.gender || 'male'
      return gender === searchForm.gender
    })
  }

  return filtered
})

const getLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    'senior': '高级教练',
    'intermediate': '中级教练',
    'junior': '初级教练'
  }
  return levelMap[level] || level
}

const getLevelTagType = (level: string) => {
  const typeMap: Record<string, string> = {
    'senior': 'danger',
    'intermediate': 'warning',
    'junior': 'success'
  }
  return typeMap[level] || 'info'
}

const loadCoachList = async () => {
  try {
    // 不限制校区，显示所有教练，不传递搜索参数到后端
    const params: any = {}
    
    // 调用获取教练列表API（不进行服务端搜索）
    const response = await coachApi.getCoaches(params)

    allCoaches.value = response.data || response
  } catch (error) {
    console.error('加载教练列表失败:', error)
    ElMessage.error('加载教练列表失败')

    // 如果API失败，使用静态数据作为后备
    allCoaches.value = [
      {
        id: 1,
        name: '张教练',
        level: 'senior',
        hourly_rate: 200,
        gender: 'male',
        age: 30,
        avatar: '',
        user: {
          real_name: '张教练',
          gender: 'male',
          age: 30
        }
      },
      {
        id: 2,
        name: '李教练',
        level: 'intermediate',
        hourly_rate: 150,
        gender: 'female',
        age: 28,
        avatar: '',
        user: {
          real_name: '李教练',
          gender: 'female',
          age: 28
        }
      }
    ]
  }
}

const handleSearch = () => {
  // 搜索现在通过计算属性自动进行，不需要重新请求数据
  // 可以在这里添加搜索统计或其他逻辑
  console.log('搜索结果数量:', coachList.value.length)
}

const resetSearch = () => {
  Object.assign(searchForm, { name: '', gender: '' })
  // 重置后计算属性会自动更新显示所有教练
}

const selectCoach = async (coach: any) => {
  try {
    // 先获取当前学生的所有预约，用于检查是否可以预约新教练
    const bookingsResponse = await bookingApi.getBookings()
    const existingBookings = Array.isArray(bookingsResponse) ? bookingsResponse : (bookingsResponse.data || [])
    
    // 筛选出所有未取消和未拒绝的预约
    const validBookings = existingBookings.filter((b: any) => 
      b.status !== 'cancelled' && b.status !== 'rejected'
    )
    
    // 获取已预约的教练ID列表（去重）
    const bookedCoachIds = [...new Set(validBookings.map((b: any) => b.coach_id))]
    
    // 如果当前教练不在已预约教练列表中，且已预约教练数已达到2个，则拒绝预约
    if (!bookedCoachIds.includes(coach.id) && bookedCoachIds.length >= 2) {
      ElMessage.error('您的预约列表中已有两个不同的教练，不能再预约新教练。请先取消其中一个教练的预约后再试。')
      return
    }
    
    // 条件满足，可以跳转到预约页面
    router.push({
      path: '/student/booking',
      query: {
        coachId: coach.id,
        coachName: coach.user?.real_name || '教练',
        hourlyRate: coach.hourly_rate
      }
    })
  } catch (error) {
    console.error('检查预约资格失败:', error)
    ElMessage.error('检查预约资格失败，请重试')
  }
}

const openCoachDetail = async (coach: any) => {
  currentCoach.value = coach
  detailVisible.value = true
  coachStats.value = null
  loading.value = true

  try {
    // 获取教练评价统计
    const response = await commentApi.getCoachCommentStats(coach.id)
    coachStats.value = response.data || response
  } catch (error) {
    console.error('获取教练评价统计失败:', error)
    ElMessage.error('获取教练评价统计失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCoachList()
})
</script>

<style scoped>
.search-bar {
  margin-bottom: 20px;
}

.coach-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.coach-info {
  display: flex;
  margin-bottom: 15px;
}

.coach-avatar {
  margin-right: 15px;
}

.coach-details h3 {
  margin: 0 0 10px 0;
}

.coach-details p {
  margin: 5px 0;
}

.coach-actions {
  text-align: center;
}

/* 教练详情样式 */
.coach-detail-content {
  padding: 0 20px;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section h3 {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.rating-stats {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.average-rating {
  text-align: center;
  margin-bottom: 20px;
}

.rating-number {
  font-size: 36px;
  font-weight: bold;
  color: #f7ba2a;
  margin-right: 10px;
}

.total-comments {
  color: #909399;
  margin-left: 10px;
}

.rating-distribution {
  margin-top: 20px;
}

.rating-bar {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.rating-label {
  width: 50px;
  margin-right: 10px;
  text-align: right;
}

.rating-bar .el-progress {
  flex: 1;
}

.comment-item {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 10px;
}

.comment-content {
  margin: 10px 0;
  color: #333;
}

.comment-info {
  color: #909399;
  font-size: 0.9em;
}

.loading-section {
  padding: 20px;
}
</style>
