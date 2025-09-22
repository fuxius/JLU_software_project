import request from '@/utils/request'

// 教练相关API
export const coachApi = {
  // 获取教练列表
  getCoaches: (params?: { 
    campus_id?: number
    level?: string
    skip?: number
    limit?: number 
  }) => {
    return request.get('/coaches', { params })
  },

  // 搜索教练
  searchCoaches: (params: {
    name?: string
    gender?: string
    age_min?: number
    age_max?: number
    campus_id?: number
  }) => {
    return request.get('/coaches/search', { params })
  },

  // 获取教练详情
  getCoach: (id: number) => {
    return request.get(`/coaches/${id}`)
  },

  // 更新教练信息
  updateCoach: (id: number, data: any) => {
    return request.put(`/coaches/${id}`, data)
  },

  // 审核教练
  approveCoach: (id: number, approved: boolean) => {
    return request.post(`/coaches/${id}/approve`, { approved })
  },

  // 获取教练的学员列表
  getCoachStudents: (id: number) => {
    return request.get(`/coaches/${id}/students`)
  },

  // 获取我的学员列表（当前登录教练）
  getMyStudents: () => {
    return request.get('/coaches/my-students')
  },

  // 获取教练课表
  getCoachSchedule: (id: number, params?: {
    date_from?: string
    date_to?: string
  }) => {
    return request.get(`/coaches/${id}/schedule`, { params })
  }
}
