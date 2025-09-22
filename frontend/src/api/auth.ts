import request from '@/utils/request'
import type { LoginForm, RegisterForm, User } from '@/types'

// 认证相关API
export const authApi = {
  // 用户登录
  login: (data: LoginForm) => {
    return request.post('/auth/login', data)
  },

  // 学员注册
  registerStudent: (data: RegisterForm) => {
    return request.post('/auth/register/student', data)
  },

  // 教练注册
  registerCoach: (data: RegisterForm) => {
    return request.post('/auth/register/coach', data)
  },

  // 获取当前用户信息
  getCurrentUser: () => {
    return request.get('/users/me')
  },

  // 更新当前用户信息
  updateCurrentUser: (data: Partial<User>) => {
    return request.put('/users/me', data)
  },

  // 修改密码
  changePassword: (data: { old_password: string; new_password: string }) => {
    return request.post('/users/change-password', data)
  }
}
