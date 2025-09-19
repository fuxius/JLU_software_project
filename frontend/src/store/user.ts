import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, LoginForm, UserRole } from '@/types'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string>('')
  const isLoggedIn = ref<boolean>(false)

  // 计算属性
  const userRole = computed(() => user.value?.role)
  const isSuperAdmin = computed(() => userRole.value === 'super_admin')
  const isCampusAdmin = computed(() => userRole.value === 'campus_admin')
  const isCoach = computed(() => userRole.value === 'coach')
  const isStudent = computed(() => userRole.value === 'student')
  const isAdmin = computed(() => isSuperAdmin.value || isCampusAdmin.value)

  // 登录
  const login = async (loginForm: LoginForm) => {
    try {
      const response = await authApi.login(loginForm)
      const { access_token, user: userInfo } = response
      
      // 保存token和用户信息
      token.value = access_token
      user.value = userInfo
      isLoggedIn.value = true
      
      // 保存到localStorage
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userInfo))
      
      ElMessage.success('登录成功')
      return { success: true }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '登录失败')
      return { success: false, message: error.response?.data?.message || '登录失败' }
    }
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = ''
    isLoggedIn.value = false
    
    // 清除localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // 跳转到登录页
    window.location.href = '/login'
  }

  // 检查登录状态
  const checkLoginStatus = async () => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      try {
        token.value = savedToken
        user.value = JSON.parse(savedUser)
        isLoggedIn.value = true
        
        // 验证token是否有效
        await authApi.getCurrentUser()
      } catch (error) {
        // token无效，清除状态
        logout()
      }
    }
  }

  // 更新用户信息
  const updateUserInfo = async (userData: Partial<User>) => {
    try {
      const response = await authApi.updateCurrentUser(userData)
      user.value = response
      
      // 更新localStorage
      localStorage.setItem('user', JSON.stringify(response))
      
      ElMessage.success('信息更新成功')
      return { success: true }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '更新失败')
      return { success: false, message: error.response?.data?.message || '更新失败' }
    }
  }

  // 修改密码
  const changePassword = async (oldPassword: string, newPassword: string) => {
    try {
      await authApi.changePassword({
        old_password: oldPassword,
        new_password: newPassword
      })
      
      ElMessage.success('密码修改成功，请重新登录')
      logout()
      return { success: true }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '密码修改失败')
      return { success: false, message: error.response?.data?.message || '密码修改失败' }
    }
  }

  return {
    // 状态
    user,
    token,
    isLoggedIn,
    
    // 计算属性
    userRole,
    isSuperAdmin,
    isCampusAdmin,
    isCoach,
    isStudent,
    isAdmin,
    
    // 方法
    login,
    logout,
    checkLoginStatus,
    updateUserInfo,
    changePassword
  }
})
