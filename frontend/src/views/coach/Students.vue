<template>
  <div class="coach-students">
    <el-card>
      <template #header>
        <span>我的学员</span>
      </template>
      
      <el-table :data="studentList" stripe>
        <el-table-column prop="name" label="学员姓名" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="age" label="年龄" />
        <el-table-column prop="gender" label="性别">
          <template #default="scope">
            {{ scope.row.gender === 'male' ? '男' : '女' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="建立关系时间" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button type="primary" size="small" @click="viewStudent(scope.row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { coachApi } from '@/api/coaches'

const studentList = ref([])

const loadStudentList = async () => {
  try {
    const students = await coachApi.getMyStudents()
    studentList.value = students.map((student: any) => ({
      id: student.id,
      name: student.user?.real_name || student.name || '学员',
      phone: student.user?.phone || '未提供',
      age: student.user?.age || 0,
      gender: student.user?.gender || 'male',
      created_at: student.created_at ? new Date(student.created_at).toLocaleString() : '未知'
    }))
  } catch (error) {
    console.error('加载学员列表失败:', error)
    ElMessage.error('加载学员列表失败')
    
    // 如果API失败，使用静态数据作为后备
    studentList.value = [
      {
        id: 1,
        name: '小明',
        phone: '13800138001',
        age: 20,
        gender: 'male',
        created_at: '2024-01-01 10:00:00'
      }
    ]
  }
}

const viewStudent = (student: any) => {
  ElMessage.info(`查看学员详情：${student.name}`)
}

onMounted(() => {
  loadStudentList()
})
</script>
