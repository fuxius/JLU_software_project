<template>
  <div class="student-competitions">
    <el-card>
      <template #header>
        <span>比赛报名</span>
      </template>
      
      <div class="competition-list">
        <div v-for="competition in competitionList" :key="competition.id" class="competition-card">
          <el-card shadow="hover">
            <h3>{{ competition.title || competition.name }}</h3>
            <p>报名费：{{ competition.registration_fee || competition.fee }}元</p>
            <p>比赛时间：{{ competition.competition_date || competition.date }}</p>
            <div class="group-select">
              <el-select v-model="groupSelectMap[competition.id]" placeholder="选择组别" size="small" style="width: 120px;">
                <el-option label="甲组" value="A" />
                <el-option label="乙组" value="B" />
                <el-option label="丙组" value="C" />
              </el-select>
            </div>
            <div class="actions">
              <el-button type="primary" @click="registerCompetition(competition)">报名</el-button>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>我的报名</span>
      </template>
      
      <el-table :data="myRegistrations" stripe>
        <el-table-column prop="competition_name" label="比赛名称" />
        <el-table-column prop="group" label="组别" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="created_at" label="报名时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { competitionApi } from '@/api/competitions'

const competitionList = ref([])
const groupSelectMap = reactive<Record<number, string>>({})
const myRegistrations = ref([])

const loadCompetitions = async () => {
  try {
    const response = await competitionApi.getCompetitions()
    competitionList.value = response
  } catch (error) {
    console.error('加载比赛列表失败:', error)
    ElMessage.error('加载比赛列表失败')
  }
}

const loadMyRegistrations = async () => {
  try {
    // 获取所有比赛的报名记录
    const competitions = competitionList.value
    const allRegistrations = []

    for (const competition of competitions) {
      try {
        const registrations = await competitionApi.getRegistrations(competition.id)
        // 只添加当前用户的报名记录
        const userRegistrations = registrations.filter((reg: any) =>
          reg.student_id === 1 // TODO: 从用户store获取实际用户ID
        )
        allRegistrations.push(...userRegistrations)
      } catch (error) {
        console.error(`加载比赛${competition.id}的报名记录失败:`, error)
      }
    }

    myRegistrations.value = allRegistrations
  } catch (error) {
    console.error('加载我的报名失败:', error)
    ElMessage.error('加载我的报名失败')
  }
}

const registerCompetition = async (competition: any) => {
  try {
    const groupType = groupSelectMap[competition.id] || 'A'
    await competitionApi.registerCompetition(competition.id, groupType)
    const groupMap: any = { A: '甲', B: '乙', C: '丙' }
    ElMessage.success(`已报名比赛：${competition.title || competition.name}（${groupMap[groupType]}组）`)
    await loadMyRegistrations()
  } catch (error: any) {
    console.error('报名失败:', error)
    ElMessage.error(error.response?.data?.detail || error.message || '报名失败')
  }
}

onMounted(() => {
  loadCompetitions()
  loadMyRegistrations()
})
</script>

<style scoped>
.competition-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.competition-card h3 {
  margin: 0 0 10px 0;
}

.competition-card p {
  margin: 5px 0;
}

.actions {
  text-align: center;
  margin-top: 15px;
}
</style>
