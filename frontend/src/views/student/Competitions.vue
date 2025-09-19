<template>
  <div class="student-competitions">
    <el-card>
      <template #header>
        <span>比赛报名</span>
      </template>
      
      <div class="competition-list">
        <div v-for="competition in competitionList" :key="competition.id" class="competition-card">
          <el-card shadow="hover">
            <h3>{{ competition.name }}</h3>
            <p>报名费：{{ competition.fee }}元</p>
            <p>比赛时间：{{ competition.date }}</p>
            <p>组别：{{ competition.groups.join('、') }}</p>
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const competitionList = ref([])
const myRegistrations = ref([])

const loadCompetitions = async () => {
  // TODO: 调用获取比赛列表API
  competitionList.value = [
    {
      id: 1,
      name: '2024年1月月赛',
      fee: 30,
      date: '2024-01-28',
      groups: ['甲组', '乙组', '丙组']
    }
  ]
}

const loadMyRegistrations = async () => {
  // TODO: 调用获取我的报名API
  myRegistrations.value = []
}

const registerCompetition = (competition: any) => {
  ElMessage.success(`已报名比赛：${competition.name}`)
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
