import request from './request'
import type { Campus } from '@/types'

// 校区相关API
export const campusApi = {
  // 获取所有校区
  getCampuses: (params?: { skip?: number; limit?: number }) => {
    return request.get('/campus', { params })
  },

  // 获取校区详情
  getCampus: (id: number) => {
    return request.get(`/campus/${id}`)
  },

  // 获取中心校区
  getMainCampus: () => {
    return request.get('/campus/main')
  },

  // 创建校区
  createCampus: (data: Partial<Campus>) => {
    return request.post('/campus', data)
  },

  // 更新校区
  updateCampus: (id: number, data: Partial<Campus>) => {
    return request.put(`/campus/${id}`, data)
  },

  // 删除校区
  deleteCampus: (id: number) => {
    return request.delete(`/campus/${id}`)
  },

  // 指定校区管理员
  assignAdmin: (campusId: number, adminId: number) => {
    return request.post(`/campus/${campusId}/assign-admin/${adminId}`)
  }
}
