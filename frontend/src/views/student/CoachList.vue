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
                <h3>{{ coach.name }}</h3>
                <p><el-tag :type="getLevelTagType(coach.level)">{{ getLevelText(coach.level) }}</el-tag></p>
                <p>收费：{{ coach.hourly_rate }}元/小时</p>
                <p>性别：{{ coach.gender === 'male' ? '男' : '女' }}</p>
                <p>年龄：{{ coach.age }}岁</p>
              </div>
            </div>
            <div class="coach-actions">
              <el-button type="primary" @click="selectCoach(coach)">选择教练</el-button>
              <el-button @click="viewCoachDetail(coach)">查看详情</el-button>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { coachApi } from '@/api/coaches'

const router = useRouter()

const searchForm = reactive({
  name: '',
  gender: ''
})

const coachList = ref([])

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
  // TODO: 调用获取教练列表API
  coachList.value = [
    {
      id: 1,
      name: '张教练',
      level: 'senior',
      hourly_rate: 200,
      gender: 'male',
      age: 30,
      avatar: ''
    },
    {
      id: 2,
      name: '李教练',
      level: 'intermediate',
      hourly_rate: 150,
      gender: 'female',
      age: 28,
      avatar: ''
    }
  ]
}

const handleSearch = () => {
  loadCoachList()
}

const resetSearch = () => {
  Object.assign(searchForm, { name: '', gender: '' })
  loadCoachList()
}

const selectCoach = (coach: any) => {
  // 跳转到预约页面，并传递教练信息
  router.push({
    path: '/student/booking',
    query: {
      coachId: coach.id,
      coachName: coach.name,
      hourlyRate: coach.hourly_rate
    }
  })
}

const viewCoachDetail = (coach: any) => {
  // TODO: 跳转到教练详情页面
  ElMessage.info(`查看教练详情：${coach.name}`)
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
