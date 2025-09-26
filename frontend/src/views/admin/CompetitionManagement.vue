<template>
  <div class="competition-management">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>比赛管理</span>
          <el-button
            v-if="!isSuperAdmin"
            type="primary"
            @click="showCreateDialog = true"
          >
            <el-icon><Plus /></el-icon>
            创建比赛
          </el-button>
          <el-tag v-if="isSuperAdmin" type="info">
            超级管理员只能查看比赛，不能创建
          </el-tag>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="状态:">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="即将开始" value="upcoming" />
            <el-option label="报名中" value="registration" />
            <el-option label="抽签完成" value="draw_complete" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已结束" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadCompetitions">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 比赛列表 -->
      <el-table
        v-loading="loading"
        :data="competitions"
        style="width: 100%"
        row-key="id"
        @expand-change="handleExpandChange"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="registration-details">
              <el-tabs v-model="activeTab" type="card">
                <el-tab-pane label="甲组报名" name="A">
                  <div>甲组报名人员信息加载中...</div>
                </el-tab-pane>
                <el-tab-pane label="乙组报名" name="B">
                  <div>乙组报名人员信息加载中...</div>
                </el-tab-pane>
                <el-tab-pane label="丙组报名" name="C">
                  <div>丙组报名人员信息加载中...</div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="title" label="比赛名称" min-width="150" />
        
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="competition_date" label="比赛日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.competition_date) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="registration_deadline" label="报名截止" width="120">
          <template #default="{ row }">
            {{ formatDate(row.registration_deadline) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="registration_fee" label="报名费" width="100">
          <template #default="{ row }">
            ¥{{ row.registration_fee }}
          </template>
        </el-table-column>
        
        <el-table-column prop="registered_count" label="报名人数" width="100">
          <template #default="{ row }">
            {{ row.registered_count }}/{{ row.max_participants }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="editCompetition(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'registration'"
              type="warning"
              size="small"
              @click="generateDraw(row)"
            >
              生成对阵
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        :current-page="pagination.page"
        :page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 创建/编辑比赛对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingCompetition ? '编辑比赛' : '创建比赛'"
      width="600px"
    >
      <el-form 
        :model="competitionForm" 
        :rules="formRules"
        ref="formRef"
        label-width="120px"
      >
        <el-form-item label="比赛标题" prop="title">
          <el-input 
            v-model="competitionForm.title" 
            placeholder="请输入比赛标题"
          />
        </el-form-item>

        <el-form-item label="比赛描述" prop="description">
          <el-input 
            v-model="competitionForm.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入比赛描述"
          />
        </el-form-item>

        <el-form-item label="校区" prop="campus_id">
          <el-select 
            v-model="competitionForm.campus_id" 
            placeholder="请选择校区"
            style="width: 100%"
          >
            <el-option 
              v-for="campus in campusList" 
              :key="campus.id" 
              :label="campus.name" 
              :value="campus.id" 
            />
          </el-select>
        </el-form-item>
          <el-form-item label="比赛状态" prop="status">
            <el-select v-model="competitionForm.status" placeholder="请选择比赛状态" style="width: 100%">
              <el-option label="即将开始" value="upcoming" />
              <el-option label="报名中" value="registration" />
              <el-option label="抽签完成" value="draw_complete" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已结束" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>

        <el-form-item label="比赛日期" prop="competition_date">
          <el-date-picker
            v-model="competitionForm.competition_date"
            type="datetime"
            placeholder="请选择比赛日期"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="报名截止时间" prop="registration_deadline">
          <el-date-picker
            v-model="competitionForm.registration_deadline"
            type="datetime"
            placeholder="请选择报名截止时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="报名费用" prop="registration_fee">
          <el-input-number
            v-model="competitionForm.registration_fee"
            :min="0"
            :step="10"
            placeholder="请输入报名费用"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="最大参与人数" prop="max_participants">
          <el-input-number
            v-model="competitionForm.max_participants"
            :min="2"
            :max="200"
            placeholder="请输入最大参与人数"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingCompetition ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { competitionApi } from '../../api/competitions'
import { campusApi } from '../../api/campus'
import { useUserStore } from '../../store/user'
import type { Campus } from '../../types'

// 用户状态
const userStore = useUserStore()
const { isSuperAdmin } = userStore

// 简化的类型定义，避免导入问题
interface CompetitionResponse {
  id: number
  title: string
  status: string
  competition_date: string
  registration_deadline: string
  registration_fee: number
  registered_count?: number
  max_participants: number
}

// 数据
const loading = ref(false)
const competitions = ref<CompetitionResponse[]>([])
const showCreateDialog = ref(false)
const editingCompetition = ref<CompetitionResponse | null>(null)
const activeTab = ref('A')
const submitting = ref(false)
const formRef = ref()
const campusList = ref<Campus[]>([]) // 校区列表

// 比赛表单数据
const competitionForm = reactive({
  title: '',
  description: '',
  campus_id: userStore.user?.campus_id || 1, // 默认使用当前用户的校区
  competition_date: '',
  registration_deadline: '',
  registration_fee: 0,
  max_participants: 32,
  status: 'upcoming'
})

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入比赛标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度应在2-100个字符之间', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入比赛描述', trigger: 'blur' }
  ],
  campus_id: [
    { required: true, message: '请选择校区', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择比赛状态', trigger: 'change' }
  ],
  competition_date: [
    { required: true, message: '请选择比赛日期', trigger: 'change' }
  ],
  registration_deadline: [
    { required: true, message: '请选择报名截止时间', trigger: 'change' }
  ],
  registration_fee: [
    { required: true, message: '请输入报名费用', trigger: 'blur' }
  ],
  max_participants: [
    { required: true, message: '请输入最大参与人数', trigger: 'blur' }
  ]
}

// 搜索表单
const searchForm = reactive({
  status: '',
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 状态映射
const statusMap = {
  'upcoming': { text: '即将开始', type: 'info' },
  'registration': { text: '报名中', type: 'success' },
  'draw_complete': { text: '抽签完成', type: 'warning' },
  'in_progress': { text: '进行中', type: 'primary' },
  'completed': { text: '已结束', type: '' },
  'cancelled': { text: '已取消', type: 'danger' }
}

// 方法
const loadCompetitions = async () => {
  try {
    loading.value = true
    const response = await competitionApi.getCompetitions({
      page: pagination.page,
      size: pagination.size,
      status: searchForm.status || undefined
    })
    
    const data = response.data || response
    competitions.value = Array.isArray(data) ? data : []
    
    // 对于简单数组响应，使用数组长度作为总数
    pagination.total = competitions.value.length
    
    console.log('加载的比赛列表:', competitions.value)
  } catch (error) {
    console.error('加载比赛列表失败:', error)
    ElMessage.error('加载比赛列表失败')
    
    // 如果API失败，使用模拟数据作为后备
    const mockData: CompetitionResponse[] = [
      {
        id: 1,
        title: '校园乒乓球春季赛',
        status: 'registration',
        competition_date: '2024-04-15T10:00:00Z',
        registration_deadline: '2024-04-10T23:59:59Z',
        registration_fee: 30,
        registered_count: 15,
        max_participants: 32
      },
      {
        id: 2,
        title: '新生乒乓球友谊赛',
        status: 'upcoming',
        competition_date: '2024-04-20T14:00:00Z',
        registration_deadline: '2024-04-18T23:59:59Z',
        registration_fee: 20,
        registered_count: 8,
        max_participants: 16
      }
    ]
    
    competitions.value = mockData
    pagination.total = mockData.length
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.status = ''
  pagination.page = 1
  loadCompetitions()
}

const editCompetition = (competition: CompetitionResponse) => {
  Object.assign(competitionForm, {
    title: competition.title,
    description: competition.description,
    campus_id: competition.campus_id,
    competition_date: competition.competition_date,
    registration_deadline: competition.registration_deadline,
    registration_fee: competition.registration_fee,
    max_participants: competition.max_participants,
    status: competition.status
  })
  editingCompetition.value = competition
  showCreateDialog.value = true
  formRef.value?.clearValidate()
}

const generateDraw = async (competition: CompetitionResponse) => {
  try {
    await ElMessageBox.confirm(
      `确定要为比赛"${competition.title}"生成对阵吗？此操作不可撤销。`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 为每个组别生成对阵
    const groups = ['A', 'B', 'C']
    let successCount = 0
    
    for (const group of groups) {
      try {
        await competitionApi.generateDraw(competition.id, group)
        successCount++
      } catch (error) {
        console.error(`生成${group}组对阵失败:`, error)
      }
    }
    
    if (successCount > 0) {
      ElMessage.success(`成功生成 ${successCount} 个组别的对阵`)
      loadCompetitions()
    } else {
      ElMessage.error('生成对阵失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('生成对阵失败:', error)
      ElMessage.error('生成对阵失败')
    }
  }
}

const handleExpandChange = (row: CompetitionResponse, expanded: boolean) => {
  if (expanded) {
    console.log('展开比赛:', row.title)
  }
}

// 表单提交处理
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 验证日期逻辑
    const competitionDate = new Date(competitionForm.competition_date)
    const deadlineDate = new Date(competitionForm.registration_deadline)
    const now = new Date()
    
    if (competitionDate <= now) {
      ElMessage.error('比赛日期必须是未来时间')
      return
    }
    
    if (deadlineDate >= competitionDate) {
      ElMessage.error('报名截止时间必须早于比赛时间')
      return
    }
    
    if (editingCompetition.value) {
      // 编辑模式
      await competitionApi.updateCompetition(editingCompetition.value.id, {
        title: competitionForm.title,
        description: competitionForm.description,
        campus_id: competitionForm.campus_id,
        competition_date: competitionForm.competition_date,
        registration_deadline: competitionForm.registration_deadline,
        registration_fee: competitionForm.registration_fee,
        max_participants: competitionForm.max_participants,
        status: competitionForm.status
      })
      ElMessage.success('比赛信息已更新')
    } else {
      // 创建模式
      await competitionApi.createCompetition({
        title: competitionForm.title,
        description: competitionForm.description,
        campus_id: competitionForm.campus_id,
        competition_date: competitionForm.competition_date,
        registration_deadline: competitionForm.registration_deadline,
        registration_fee: competitionForm.registration_fee,
        max_participants: competitionForm.max_participants,
        status: competitionForm.status
      })
      ElMessage.success('比赛创建成功')
    }
    showCreateDialog.value = false
    resetForm()
    loadCompetitions() // 重新加载列表
    
  } catch (error: any) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(competitionForm, {
    title: '',
    description: '',
    campus_id: userStore.user?.campus_id || 1,
    competition_date: '',
    registration_deadline: '',
    registration_fee: 0,
    max_participants: 32
  })
  editingCompetition.value = null
  formRef.value?.clearValidate()
}

const handleCancel = () => {
  showCreateDialog.value = false
  resetForm()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadCompetitions()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadCompetitions()
}

const getStatusType = (status: string) => {
  return statusMap[status as keyof typeof statusMap]?.type || ''
}

const getStatusText = (status: string) => {
  return statusMap[status as keyof typeof statusMap]?.text || status
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 获取校区列表
const fetchCampuses = async () => {
  try {
    const response = await campusApi.getCampuses()
    campusList.value = response.data?.items || response.data || []
    console.log('校区列表:', campusList.value)
  } catch (error) {
    console.error('获取校区列表失败:', error)
    ElMessage.error('获取校区列表失败')
  }
}

// 生命周期
onMounted(() => {
  loadCompetitions()
  fetchCampuses()
})
</script>

<style scoped>
.competition-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.registration-details {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 6px;
}

.registration-details h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

:deep(.el-pagination) {
  margin-top: 20px;
  text-align: center;
}
</style>