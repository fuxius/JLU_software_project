<template>
  <div class="coach-evaluations">
    <el-card>
      <template #header>
        <span>课后评价</span>
      </template>
      
      <el-table :data="evaluationList" stripe>
        <el-table-column prop="student_name" label="学员" />
        <el-table-column prop="course_date" label="课程日期" />
        <el-table-column prop="student_feedback" label="学员反馈" />
        <el-table-column prop="coach_feedback" label="教练评价" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button 
              v-if="!scope.row.coach_feedback"
              type="primary" 
              size="small" 
              @click="addEvaluation(scope.row)"
            >
              添加评价
            </el-button>
            <el-button 
              v-else
              type="info" 
              size="small" 
              @click="editEvaluation(scope.row)"
            >
              编辑评价
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 评价对话框 -->
    <el-dialog
      title="课后评价"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form :model="evaluationForm" label-width="100px">
        <el-form-item label="学员">
          <el-input v-model="evaluationForm.student_name" disabled />
        </el-form-item>
        <el-form-item label="课程日期">
          <el-input v-model="evaluationForm.course_date" disabled />
        </el-form-item>
        <el-form-item label="教练评价">
          <el-input 
            v-model="evaluationForm.coach_feedback" 
            type="textarea" 
            :rows="4"
            placeholder="请输入对学员的评价和建议"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveEvaluation">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const evaluationList = ref([])
const dialogVisible = ref(false)
const evaluationForm = reactive({
  id: null,
  student_name: '',
  course_date: '',
  coach_feedback: ''
})

const loadEvaluationList = async () => {
  // TODO: 调用获取评价列表API
  evaluationList.value = [
    {
      id: 1,
      student_name: '小明',
      course_date: '2024-01-15',
      student_feedback: '今天学习了正手攻球，收获很大',
      coach_feedback: ''
    }
  ]
}

const addEvaluation = (row: any) => {
  Object.assign(evaluationForm, {
    id: row.id,
    student_name: row.student_name,
    course_date: row.course_date,
    coach_feedback: ''
  })
  dialogVisible.value = true
}

const editEvaluation = (row: any) => {
  Object.assign(evaluationForm, row)
  dialogVisible.value = true
}

const saveEvaluation = () => {
  // TODO: 调用保存评价API
  ElMessage.success('评价保存成功')
  dialogVisible.value = false
  loadEvaluationList()
}

onMounted(() => {
  loadEvaluationList()
})
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>
