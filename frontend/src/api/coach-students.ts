import request from './request'

// 教练学员关系相关类型定义
export interface CoachStudentCreate {
  coach_id: number
  application_message?: string
}

export interface CoachStudentResponse {
  id: number
  coach_id: number
  student_id: number
  status: string
  application_message?: string
  response_message?: string
  applied_at: string
  responded_at?: string
  created_at: string
  updated_at?: string
  // 关联信息
  coach?: {
    id: number
    user: {
      real_name: string
      avatar_url?: string
    }
    level: string
    hourly_rate: number
    achievements?: string
    approval_status: string
  }
  student?: {
    id: number
    user: {
      real_name: string
      avatar_url?: string
    }
  }
}

export interface ChangeCoachRequest {
  current_coach_id: number
  new_coach_id: number
  reason: string
}

export interface ApprovalRequest {
  approved: boolean
  response_message?: string
}

export interface CoachStudentQuery {
  status?: string
  coach_id?: number
  student_id?: number
  skip?: number
  limit?: number
}

// 教练学员关系API
export const coachStudentApi = {
  // 学员申请选择教练
  applyCoach: (data: CoachStudentCreate) => {
    return request.post<CoachStudentResponse>('/coach-students', data)
  },

  // 获取学员的教练关系列表
  getStudentCoaches: (studentId: number, params?: CoachStudentQuery) => {
    return request.get<CoachStudentResponse[]>(`/coach-students/student/${studentId}`, { params })
  },

  // 获取教练的学员关系列表
  getCoachStudents: (coachId: number, params?: CoachStudentQuery) => {
    return request.get<CoachStudentResponse[]>(`/coach-students/coach/${coachId}`, { params })
  },

  // 获取我的教练列表（当前学员）
  getMyCoaches: (params?: CoachStudentQuery) => {
    return request.get<CoachStudentResponse[]>('/coach-students/my-coaches', { params })
  },

  // 获取我的学员列表（当前教练）
  getMyStudents: (params?: CoachStudentQuery) => {
    return request.get<CoachStudentResponse[]>('/coach-students/my-students', { params })
  },

  // 教练审核学员申请
  approveApplication: (relationId: number, data: ApprovalRequest) => {
    return request.put<CoachStudentResponse>(`/coach-students/${relationId}/approve`, data)
  },

  // 申请更换教练
  changeCoach: (data: ChangeCoachRequest) => {
    return request.post<{ message: string }>('/coach-students/change-coach', data)
  },

  // 获取待审核申请列表（教练）
  getPendingApprovals: (params?: { skip?: number; limit?: number }) => {
    return request.get<CoachStudentResponse[]>('/coach-students/pending-approvals', { params })
  },

  // 删除教练学员关系
  removeRelation: (relationId: number) => {
    return request.delete(`/coach-students/${relationId}`)
  },

  // 获取关系状态文本
  getStatusText: (status: string) => {
    const statusMap: Record<string, string> = {
      'pending': '待审核',
      'approved': '已通过',
      'rejected': '已拒绝',
      'expired': '已过期'
    }
    return statusMap[status] || status
  },

  // 获取关系状态颜色
  getStatusColor: (status: string) => {
    const colorMap: Record<string, string> = {
      'pending': 'warning',
      'approved': 'success',
      'rejected': 'danger',
      'expired': 'info'
    }
    return colorMap[status] || 'default'
  },

  // 检查学员是否可以申请更多教练
  canApplyMoreCoaches: (currentCoachCount: number) => {
    return currentCoachCount < 2 // 学员最多选择2个教练
  },

  // 检查教练是否可以接受更多学员
  canAcceptMoreStudents: (currentStudentCount: number) => {
    return currentStudentCount < 20 // 教练最多指导20个学员
  },

  // 格式化申请时间
  formatApplyTime: (time: string) => {
    return new Date(time).toLocaleString('zh-CN')
  },

  // 获取教练级别文本
  getCoachLevelText: (level: string) => {
    const levelMap: Record<string, string> = {
      'junior': '初级教练',
      'intermediate': '中级教练',
      'senior': '高级教练'
    }
    return levelMap[level] || level
  },

  // 获取教练级别颜色
  getCoachLevelColor: (level: string) => {
    const colorMap: Record<string, string> = {
      'junior': '#52c41a',
      'intermediate': '#1890ff',
      'senior': '#722ed1'
    }
    return colorMap[level] || '#666666'
  },

  // 格式化教练费用
  formatHourlyRate: (rate: number) => {
    return `¥${rate}/小时`
  }
}
