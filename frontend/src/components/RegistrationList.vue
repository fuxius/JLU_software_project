<template>
  <div class="registration-list">
    <div class="list-header">
      <span>{{ groupType }}组报名列表</span>
      <el-button
        type="primary"
        size="small"
        @click="refreshList"
        :loading="loading"
      >
        刷新
      </el-button>
    </div>
    
    <el-table
      v-loading="loading"
      :data="registrations"
      style="width: 100%"
      size="small"
    >
      <el-table-column prop="student.user.real_name" label="姓名" width="100" />
      <el-table-column prop="student.user.phone" label="电话" width="120" />
      <el-table-column prop="student.user.gender" label="性别" width="60">
        <template #default="{ row }">
          {{ row.student?.user?.gender === 'male' ? '男' : '女' }}
        </template>
      </el-table-column>
      <el-table-column prop="is_confirmed" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_confirmed ? 'success' : 'warning'" size="small">
            {{ row.is_confirmed ? '已确认' : '待确认' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="报名时间" width="120">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button
            v-if="!row.is_confirmed"
            type="success"
            size="small"
            @click="confirmRegistration(row)"
          >
            确认
          </el-button>
          <span v-else class="confirmed-text">已确认</span>
        </template>
      </el-table-column>
    </el-table>
    
    <div v-if="!loading && registrations.length === 0" class="empty-state">
      <el-empty description="暂无报名信息" :image-size="80" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { competitionApi, type CompetitionRegistrationResponse } from '../api/competitions'

interface Props {
  competitionId: number
  groupType: string
}

const props = defineProps<Props>()

const loading = ref(false)
const registrations = ref<CompetitionRegistrationResponse[]>([])

// 加载报名列表
const loadRegistrations = async () => {
  try {
    loading.value = true
    const response = await competitionApi.getRegistrations(props.competitionId, props.groupType)
    registrations.value = response.data || []
  } catch (error) {
    console.error('加载报名列表失败:', error)
    ElMessage.error('加载报名列表失败')
    registrations.value = []
  } finally {
    loading.value = false
  }
}

// 刷新列表
const refreshList = () => {
  loadRegistrations()
}

// 确认报名
const confirmRegistration = async (registration: CompetitionRegistrationResponse) => {
  try {
    await competitionApi.confirmRegistration(registration.id)
    ElMessage.success('确认成功')
    loadRegistrations()
  } catch (error) {
    console.error('确认报名失败:', error)
    ElMessage.error('确认报名失败')
  }
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 监听props变化
watch([() => props.competitionId, () => props.groupType], () => {
  if (props.competitionId && props.groupType) {
    loadRegistrations()
  }
}, { immediate: true })

onMounted(() => {
  if (props.competitionId && props.groupType) {
    loadRegistrations()
  }
})
</script>

<style scoped>
.registration-list {
  margin-top: 10px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 20px;
}

.confirmed-text {
  color: #67c23a;
  font-size: 12px;
}
</style>