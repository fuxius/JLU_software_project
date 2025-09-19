import request from './request'

// 学员相关API
export const studentApi = {
  // 获取学员列表
  getStudents: (params?: { 
    campus_id?: number
    skip?: number
    limit?: number 
  }) => {
    return request.get('/students', { params })
  },

  // 获取当前学员信息
  getCurrentStudent: () => {
    return request.get('/students/me')
  },

  // 获取学员详情
  getStudent: (id: number) => {
    return request.get(`/students/${id}`)
  },

  // 更新学员信息
  updateStudent: (id: number, data: any) => {
    return request.put(`/students/${id}`, data)
  },

  // 获取学员的教练列表
  getStudentCoaches: (id: number) => {
    return request.get(`/students/${id}/coaches`)
  },

  // 获取学员预约记录
  getStudentBookings: (id: number, params?: { status?: string }) => {
    return request.get(`/students/${id}/bookings`, { params })
  },

  // 获取学员账户余额
  getStudentBalance: (id: number) => {
    return request.get(`/students/${id}/balance`)
  }
}
