<template>
  <div class="not-found-container">
    <el-result
      icon="warning"
      title="404"
      sub-title="抱歉，您访问的页面不存在"
    >
      <template #extra>
        <el-button type="primary" @click="goHome">
          返回首页
        </el-button>
        <el-button @click="goBack">
          返回上页
        </el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

// 返回首页
const goHome = () => {
  const role = userStore.userRole
  switch (role) {
    case 'super_admin':
      router.push('/admin/campus')
      break
    case 'campus_admin':
      router.push('/admin/users')
      break
    case 'coach':
      router.push('/coach/students')
      break
    case 'student':
      router.push('/student/coaches')
      break
    default:
      router.push('/login')
  }
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 20px;
}
</style>