import request from '@/utils/request'
import type { 
  CommentCreate, 
  CommentUpdate, 
  CommentResponse, 
  CommentWithBookingInfo, 
  CoachCommentStats, 
  StudentCommentStats 
} from './comments'

// 从评论接口类型映射到评价接口类型
export interface EvaluationCreate {
  course_id: number  // 实际是 booking_id
  content: string
  rating?: number
}

export interface EvaluationUpdate {
  content?: string
  rating?: number
}

export type EvaluationResponse = CommentWithBookingInfo

export interface EvaluationQuery {
  course_id?: number  // 映射 booking_id
  evaluator_type?: string
  skip?: number
  limit?: number
}

export interface EvaluationSummary {
  total_comments: number
  average_rating: number
  rating_distribution: Record<string, number>
  recent_comments: any[]
}

export interface PendingEvaluationCourse {
  course_id: number  // 映射 booking_id
  booking_id: number
  completed_at?: string
  booking: {
    start_time: string
    end_time: string
    coach_name?: string
    student_name?: string
  }
}

// 评价相关API（使用 comments API）
export const evaluationApi = {
  // 创建评价
  createEvaluation: (data: EvaluationCreate) => {
    const commentData: CommentCreate = {
      booking_id: data.course_id,
      rating: data.rating || 5,
      content: data.content
    }
    return request.post<CommentResponse>('/comments/', commentData)
  },

  // 获取评价列表
  getEvaluations: async (params?: EvaluationQuery) => {
    // 转换参数
    const apiParams = {
      skip: params?.skip,
      limit: params?.limit,
      booking_id: params?.course_id
    }
    const response = await request.get<CommentWithBookingInfo[]>('/comments/my/comments', { params: apiParams })
    return response
  },

  // 获取评价详情
  getEvaluation: (id: number) => {
    return request.get<CommentResponse>(`/comments/${id}`)
  },

  // 更新评价
  updateEvaluation: (id: number, data: EvaluationUpdate) => {
    return request.put<CommentResponse>(`/comments/${id}`, data)
  },

  // 删除评价
  deleteEvaluation: (id: number) => {
    return request.delete(`/comments/${id}`)
  },

  // 获取课程的所有评价
  getCourseEvaluations: (courseId: number) => {
    return request.get<CommentResponse>(`/comments/booking/${courseId}`)
  },

  // 获取我的待评价课程
  getMyPendingEvaluations: () => {
    return request.get<any[]>('/bookings/my/completed')  // 我们需要获取已完成但未评价的预约
  },

  // 获取评价统计
  getEvaluationStatistics: async () => {
    const stats = await request.get<CoachCommentStats>('/comments/my/stats')
    return stats as unknown as EvaluationSummary
  },

  // 获取教练评价汇总
  getCoachEvaluationSummary: (coachId: number) => {
    return request.get<EvaluationSummary>(`/evaluations/coach/${coachId}/summary/`)
  },

  // 获取评分星级组件数据
  getRatingStars: (rating?: number) => {
    const stars = []
    const fullStars = Math.floor(rating || 0)
    const hasHalfStar = (rating || 0) % 1 >= 0.5
    
    for (let i = 1; i <= 5; i++) {
      if (i <= fullStars) {
        stars.push('full')
      } else if (i === fullStars + 1 && hasHalfStar) {
        stars.push('half')
      } else {
        stars.push('empty')
      }
    }
    
    return stars
  },

  // 格式化评分显示
  formatRating: (rating?: number) => {
    if (!rating) return '未评分'
    return `${rating.toFixed(1)} 分`
  },

  // 获取评分文本描述
  getRatingText: (rating?: number) => {
    if (!rating) return '未评分'
    if (rating >= 4.5) return '非常满意'
    if (rating >= 3.5) return '满意'
    if (rating >= 2.5) return '一般'
    if (rating >= 1.5) return '不满意'
    return '非常不满意'
  },

  // 获取评分颜色
  getRatingColor: (rating?: number) => {
    if (!rating) return '#dcdfe6'
    if (rating >= 4.5) return '#67c23a'
    if (rating >= 3.5) return '#e6a23c'
    if (rating >= 2.5) return '#f56c6c'
    if (rating >= 1.5) return '#f56c6c'
    return '#f56c6c'
  },

  // 格式化评价时间
  formatEvaluationTime: (time: string) => {
    return new Date(time).toLocaleString('zh-CN')
  },

  // 截取评价内容预览
  getContentPreview: (content: string, maxLength: number = 100) => {
    if (content.length <= maxLength) return content
    return content.substring(0, maxLength) + '...'
  },

  // 验证评价内容
  validateContent: (content: string) => {
    if (!content || content.trim().length === 0) {
      return '评价内容不能为空'
    }
    if (content.length > 2000) {
      return '评价内容不能超过2000字'
    }
    return null
  },

  // 验证评分
  validateRating: (rating?: number) => {
    if (rating !== undefined && (rating < 1 || rating > 5)) {
      return '评分必须在1-5之间'
    }
    return null
  },

  // 获取评价类型文本
  getEvaluatorTypeText: (type: string) => {
    const typeMap: Record<string, string> = {
      'student': '学员评价',
      'coach': '教练评价'
    }
    return typeMap[type] || type
  },

  // 检查是否可以编辑评价（24小时内）
  canEditEvaluation: (createdAt: string) => {
    const createTime = new Date(createdAt).getTime()
    const now = new Date().getTime()
    const hoursPassed = (now - createTime) / (1000 * 60 * 60)
    return hoursPassed < 24
  },

  // 格式化评价状态
  getEvaluationStatus: (evaluation: EvaluationResponse) => {
    if (evaluation.updated_at && evaluation.updated_at !== evaluation.created_at) {
      return '已修改'
    }
    return '原始评价'
  }
}
