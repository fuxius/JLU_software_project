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

const studentList = ref([])

const loadStudentList = async () => {
  // TODO: 调用获取学员列表API
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

const viewStudent = (student: any) => {
  ElMessage.info(`查看学员详情：${student.name}`)
}

onMounted(() => {
  loadStudentList()
})
</script>
