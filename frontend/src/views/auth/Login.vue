<template>
  <div class="login-container">
    <div class="login-form">
      <div class="login-header">
        <h1>乒乓球培训管理系统</h1>
        <p>请登录您的账户</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form-content"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            style="width: 100%"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>

        <el-form-item>
          <el-button
            type="success"
            size="large"
            style="width: 100%"
            @click="quickLogin"
          >
            快速测试登录
          </el-button>
        </el-form-item>
        
        <div class="login-footer">
          <router-link to="/register" class="register-link">
            还没有账户？立即注册
          </router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElForm, ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import type { LoginForm } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref<InstanceType<typeof ElForm>>()
const loading = ref(false)

// 表单数据
const loginForm = reactive<LoginForm>({
  username: 'lxy',
  password: 'lxy123!!'
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 16, message: '密码长度为8-16位', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true

    const result = await userStore.login(loginForm)

    if (result.success) {
      // 根据用户角色跳转到不同页面
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
          // 如果角色未识别，跳转到登录页面
          router.push('/login')
      }
    }
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}

// 快速测试登录
const quickLogin = async () => {
  try {
    loading.value = true

    // 设置测试账户信息
    loginForm.username = 'lxy'
    loginForm.password = 'lxy123!!'

    const result = await userStore.login(loginForm)

    if (result.success) {
      // 根据用户角色跳转到不同页面
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
          // 如果角色未识别，跳转到登录页面
          router.push('/login')
      }
    }
  } catch (error) {
    console.error('快速登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-form {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
  }
  
  p {
    color: #666;
    font-size: 14px;
  }
}

.login-form-content {
  .el-form-item {
    margin-bottom: 20px;
  }
  
  .el-input {
    height: 48px;
    
    :deep(.el-input__wrapper) {
      border-radius: 8px;
    }
  }
  
  .el-button {
    height: 48px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
  }
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  
  .register-link {
    color: #409eff;
    text-decoration: none;
    font-size: 14px;
    
    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
