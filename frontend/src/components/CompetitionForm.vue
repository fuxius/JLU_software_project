<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="120px"
  >
    <el-form-item label="比赛名称" prop="title">
      <el-input
        v-model="form.title"
        placeholder="请输入比赛名称"
        maxlength="200"
        show-word-limit
      />
    </el-form-item>
    
    <el-form-item label="比赛描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="3"
        placeholder="请输入比赛描述"
        maxlength="500"
        show-word-limit
      />
    </el-form-item>
    
    <el-form-item label="比赛日期" prop="competition_date">
      <el-date-picker
        v-model="form.competition_date"
        type="datetime"
        placeholder="请选择比赛日期"
        style="width: 100%"
      />
    </el-form-item>
    
    <el-form-item label="报名截止" prop="registration_deadline">
      <el-date-picker
        v-model="form.registration_deadline"
        type="datetime"
        placeholder="请选择报名截止时间"
        style="width: 100%"
      />
    </el-form-item>
    
    <el-form-item label="报名费" prop="registration_fee">
      <el-input-number
        v-model="form.registration_fee"
        :min="0"
        :precision="2"
        controls-position="right"
        style="width: 200px"
      />
      <span style="margin-left: 8px;">元</span>
    </el-form-item>
    
    <el-form-item label="最大参赛人数" prop="max_participants">
      <el-input-number
        v-model="form.max_participants"
        :min="4"
        :max="128"
        controls-position="right"
        style="width: 200px"
      />
      <span style="margin-left: 8px;">人</span>
    </el-form-item>
    
    <el-form-item label="校区" prop="campus_id" v-if="userStore.user?.role === 'SUPER_ADMIN'">
      <el-select v-model="form.campus_id" placeholder="请选择校区" style="width: 200px">
        <el-option
          v-for="campus in campuses"
          :key="campus.id"
          :label="campus.name"
          :value="campus.id"
        />
      </el-select>
    </el-form-item>
    
    <el-form-item v-if="isEdit" label="状态" prop="status">
      <el-select v-model="form.status" placeholder="请选择状态" style="width: 200px">
        <el-option label="即将开始" value="upcoming" />
        <el-option label="报名中" value="registration" />
        <el-option label="抽签完成" value="draw_complete" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="已结束" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        {{ isEdit ? '更新' : '创建' }}
      </el-button>
      <el-button @click="handleCancel">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { competitionApi, type CompetitionCreate, type CompetitionUpdate, type CompetitionResponse } from '../api/competitions'
import { campusApi, type Campus } from '../api/campus'
import { useUserStore } from '../store/user'

interface Props {
  competition?: CompetitionResponse | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  submit: []
  cancel: []
}>()

const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const campuses = ref<Campus[]>([])

// 判断是否为编辑模式
const isEdit = computed(() => !!props.competition)

// 表单数据
const form = reactive({
  title: '',
  description: '',
  competition_date: '',
  registration_deadline: '',
  registration_fee: 30,
  max_participants: 32,
  campus_id: 0,
  status: 'upcoming'
})

// 表单验证规则
const rules: FormRules = {
  title: [
    { required: true, message: '请输入比赛名称', trigger: 'blur' },
    { min: 2, max: 200, message: '比赛名称长度在2到200个字符', trigger: 'blur' }
  ],
  competition_date: [
    { required: true, message: '请选择比赛日期', trigger: 'change' }
  ],
  registration_deadline: [
    { required: true, message: '请选择报名截止时间', trigger: 'change' }
  ],
  registration_fee: [
    { required: true, message: '请输入报名费', trigger: 'blur' }
  ],
  max_participants: [
    { required: true, message: '请输入最大参赛人数', trigger: 'blur' }
  ],
  campus_id: [
    { required: true, message: '请选择校区', trigger: 'change' }
  ]
}

// 加载校区列表
const loadCampuses = async () => {
  try {
    const response = await campusApi.getCampuses()
    campuses.value = response.data || []
  } catch (error) {
    console.error('加载校区列表失败:', error)
  }
}

// 初始化表单数据
const initForm = () => {
  if (props.competition) {
    // 编辑模式，填充现有数据
    Object.assign(form, {
      title: props.competition.title,
      description: props.competition.description || '',
      competition_date: props.competition.competition_date,
      registration_deadline: props.competition.registration_deadline,
      registration_fee: props.competition.registration_fee,
      max_participants: props.competition.max_participants,
      campus_id: props.competition.campus_id,
      status: props.competition.status
    })
  } else {
    // 创建模式，设置默认值
    form.title = ''
    form.description = ''
    form.competition_date = ''
    form.registration_deadline = ''
    form.registration_fee = 30
    form.max_participants = 32
    form.campus_id = userStore.user?.campus_id || 0
    form.status = 'upcoming'
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 验证日期逻辑
    const competitionDate = new Date(form.competition_date)
    const deadlineDate = new Date(form.registration_deadline)
    
    if (deadlineDate >= competitionDate) {
      ElMessage.error('报名截止时间必须早于比赛日期')
      return
    }
    
    loading.value = true
    
    if (isEdit.value && props.competition) {
      // 更新比赛
      const updateData: CompetitionUpdate = {
        title: form.title,
        description: form.description,
        competition_date: form.competition_date,
        registration_deadline: form.registration_deadline,
        registration_fee: form.registration_fee,
        max_participants: form.max_participants,
        status: form.status
      }
      
      await competitionApi.updateCompetition(props.competition.id, updateData)
      ElMessage.success('比赛更新成功')
    } else {
      // 创建比赛
      const createData: CompetitionCreate = {
        title: form.title,
        description: form.description,
        competition_date: form.competition_date,
        registration_deadline: form.registration_deadline,
        registration_fee: form.registration_fee,
        max_participants: form.max_participants,
        campus_id: form.campus_id
      }
      
      await competitionApi.createCompetition(createData)
      ElMessage.success('比赛创建成功')
    }
    
    emit('submit')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    loading.value = false
  }
}

// 取消操作
const handleCancel = () => {
  emit('cancel')
}

// 监听props变化，重新初始化表单
watch(() => props.competition, () => {
  initForm()
}, { immediate: true })

onMounted(() => {
  loadCampuses()
  initForm()
})
</script>

<style scoped>
.el-form {
  max-width: 600px;
}
</style>