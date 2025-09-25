import request from '@/utils/request'

// 评论相关类型定义
export interface CommentCreate {
  booking_id: number
  rating: number
  content?: string
}

export interface CommentUpdate {
  rating: number
  content?: string
}

export interface CommentResponse {
  id: number
  booking_id: number
  rating: number
  content?: string
  created_at: string
  updated_at?: string
}

export interface CommentWithBookingInfo extends CommentResponse {
  coach_name?: string
  student_name?: string
  booking_start_time?: string
  booking_end_time?: string
  booking_status?: string
}

export interface CoachCommentStats {
  coach_id: number
  coach_name: string
  total_comments: number
  average_rating: number
  rating_distribution: Record<number, number>
  recent_comments: CommentWithBookingInfo[]
}

export interface StudentCommentStats {
  student_id: number
  student_name: string
  total_comments_given: number
  average_rating_given: number
  recent_comments: CommentWithBookingInfo[]
}

// 评论相关API
export const commentApi = {
  // 创建评论
  createComment: (data: CommentCreate) => {
    return request.post<CommentResponse>('/comments/', data)
  },

  // 更新评论
  updateComment: (id: number, data: CommentUpdate) => {
    return request.put<CommentResponse>(`/comments/${id}`, data)
  },

  // 删除评论
  deleteComment: (id: number) => {
    return request.delete(`/comments/${id}`)
  },

  // 获取评论详情
  getComment: (id: number) => {
    return request.get<CommentResponse>(`/comments/${id}`)
  },

  // 获取教练的评论列表
  getCommentsByCoach: (coachId: number, params?: { skip?: number; limit?: number }) => {
    return request.get<CommentWithBookingInfo[]>(`/comments/coach/${coachId}`, { params })
  },

  // 获取学员的评论列表
  getCommentsByStudent: (studentId: number, params?: { skip?: number; limit?: number }) => {
    return request.get<CommentWithBookingInfo[]>(`/comments/student/${studentId}`, { params })
  },

  // 获取教练评价统计
  getCoachCommentStats: (coachId: number) => {
    return request.get<CoachCommentStats>(`/comments/coach/${coachId}/stats`)
  },

  // 获取学员评价统计
  getStudentCommentStats: (studentId: number) => {
    return request.get<StudentCommentStats>(`/comments/student/${studentId}/stats`)
  },

  // 获取我的评论
  getMyComments: (params?: { skip?: number; limit?: number }) => {
    return request.get<CommentWithBookingInfo[]>('/comments/my/comments', { params })
  },

  // 获取我的评价统计
  getMyCommentStats: () => {
    return request.get('/comments/my/stats')
  },

  // 获取预约的评论
  getCommentByBooking: (bookingId: number) => {
    return request.get<CommentResponse>(`/comments/booking/${bookingId}`)
  }
}
