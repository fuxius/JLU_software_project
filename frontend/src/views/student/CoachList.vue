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

    <el-dialog v-model="detailVisible" title="教练详情" width="520px">
      <div v-if="currentCoach">
        <p>姓名：{{ currentCoach.user?.real_name || '-' }}</p>
        <p>级别：{{ getLevelText(currentCoach.level) }}</p>
        <p>收费：{{ currentCoach.hourly_rate }} 元/小时</p>
        <p>性别：{{ (currentCoach.user?.gender || 'male') === 'male' ? '男' : '女' }}</p>
        <p>年龄：{{ currentCoach.user?.age ?? '-' }}</p>
        <p>简介：{{ currentCoach.achievements || '暂无' }}</p>
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
import { useUserStore } from '@/store/user'

const router = useRouter()

const searchForm = reactive({
  name: '',
  gender: ''
})

const allCoaches = ref<any[]>([])  // 存储所有教练数据
const detailVisible = ref(false)
const currentCoach = ref<any | null>(null)

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

const selectCoach = (coach: any) => {
  // 跳转到预约页面，并传递教练信息
  router.push({
    path: '/student/booking',
    query: {
      coachId: coach.id,
      coachName: coach.user?.real_name || '教练',
      hourlyRate: coach.hourly_rate
    }
  })
}

const openCoachDetail = (coach: any) => {
  currentCoach.value = coach
  detailVisible.value = true
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
</style>
