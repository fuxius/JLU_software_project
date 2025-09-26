import request from '../utils/request'
import type { User, PaginatedResponse } from '../types'

// 用户管理API
export const usersApi = {
  // 获取用户列表
  getUsersList: (params: {
    skip?: number
    limit?: number
    username?: string
    real_name?: string
    role?: string
  }) => {
    return request.get('/users/', { params })
  },

  // 获取单个用户信息
  getUser: (userId: number) => {
    return request.get(`/users/${userId}`)
  },

  // 更新用户信息
  updateUser: (userId: number, data: {
    real_name?: string
    role?: string
    phone?: string
    email?: string
    gender?: string
    age?: number
  }) => {
    return request.put(`/users/${userId}`, data)
  },

  // 切换用户状态
  toggleUserStatus: (userId: number) => {
    return request.patch(`/users/${userId}/toggle-status`)
  },

  // 重置用户密码
  resetUserPassword: (userId: number) => {
    return request.post(`/users/${userId}/reset-password`)
  },

  // 停用用户
  deactivateUser: (userId: number) => {
    return request.delete(`/users/${userId}`)
  },

  // 更改用户校区
  updateUserCampus: (userId: number, campusId: number | null) => {
    return request.patch(`/users/${userId}/campus`, { campus_id: campusId })
  }
}