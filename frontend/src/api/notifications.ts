/**
 * 通知管理相关API
 */
import request from '@/utils/request'

// 通知类型枚举
export enum NotificationType {
  SYSTEM = 'system',          // 系统通知
  BOOKING = 'booking',        // 预约相关
  PAYMENT = 'payment',        // 支付相关
  COMPETITION = 'competition',  // 比赛相关
  EVALUATION = 'evaluation',  // 评价相关
  COACH_STUDENT = 'coach_student'  // 师生关系相关
}

// 通知优先级枚举
export enum NotificationPriority {
  LOW = 'low',        // 低
  NORMAL = 'normal',  // 普通
  HIGH = 'high',      // 高
  URGENT = 'urgent'   // 紧急
}

// 基础通知信息
export interface NotificationBase {
  title: string
  content: string
  type: string
  priority: string
  recipient_id: number
  resource_type?: string
  resource_id?: number
}

// 创建通知
export interface NotificationCreate extends NotificationBase {
  sender_id?: number
  send_email?: boolean
  send_sms?: boolean
  send_push?: boolean
  scheduled_at?: string
  expires_at?: string
}

// 更新通知
export interface NotificationUpdate {
  is_read?: boolean
  is_deleted?: boolean
}

// 通知响应
export interface NotificationResponse extends NotificationBase {
  id: number
  sender_id?: number
  is_read: boolean
  read_at?: string
  is_deleted: boolean
  send_email: boolean
  send_sms: boolean
  send_push: boolean
  scheduled_at?: string
  sent_at?: string
  expires_at?: string
  created_at: string
  updated_at?: string
}

// 通知查询参数
export interface NotificationQuery {
  type?: string
  is_read?: boolean
  priority?: string
  start_date?: string
  end_date?: string
  page?: number
  size?: number
}

// 通知模板
export interface NotificationTemplate {
  id: number
  code: string
  name: string
  type: string
  title_template: string
  content_template: string
  default_priority: string
  default_send_email: boolean
  default_send_sms: boolean
  default_send_push: boolean
  is_active: boolean
  created_at: string
  updated_at?: string
}

// 用户通知设置
export interface UserNotificationSettings {
  id: number
  user_id: number
  system_notifications: boolean
  booking_notifications: boolean
  payment_notifications: boolean
  competition_notifications: boolean
  evaluation_notifications: boolean
  coach_student_notifications: boolean
  email_enabled: boolean
  sms_enabled: boolean
  push_enabled: boolean
  quiet_start_time: string
  quiet_end_time: string
  weekend_quiet: boolean
  created_at: string
  updated_at?: string
}

// 更新用户通知设置
export interface UserNotificationSettingsUpdate {
  system_notifications?: boolean
  booking_notifications?: boolean
  payment_notifications?: boolean
  competition_notifications?: boolean
  evaluation_notifications?: boolean
  coach_student_notifications?: boolean
  email_enabled?: boolean
  sms_enabled?: boolean
  push_enabled?: boolean
  quiet_start_time?: string
  quiet_end_time?: string
  weekend_quiet?: boolean
}

// 通知统计
export interface NotificationStatistics {
  total_notifications: number
  unread_notifications: number
  read_notifications: number
  notifications_by_type: Array<{
    type: string
    count: number
  }>
  notifications_by_priority: Array<{
    priority: string
    count: number
  }>
}

// 批量通知
export interface BulkNotificationCreate {
  title: string
  content: string
  type: string
  priority: string
  recipient_ids: number[]
  send_email?: boolean
  send_sms?: boolean
  send_push?: boolean
  scheduled_at?: string
  expires_at?: string
}

export const notificationApi = {
  // 创建通知
  createNotification: (data: NotificationCreate) => {
    return request.post<NotificationResponse>('/notifications', data)
  },

  // 批量发送通知
  createBulkNotifications: (data: BulkNotificationCreate) => {
    return request.post<NotificationResponse[]>('/notifications/bulk', data)
  },

  // 获取通知列表
  getNotifications: (params?: NotificationQuery) => {
    return request.get<NotificationResponse[]>('/notifications', { params })
  },

  // 获取通知详情
  getNotification: (id: number) => {
    return request.get<NotificationResponse>(`/notifications/${id}`)
  },

  // 更新通知状态
  updateNotification: (id: number, data: NotificationUpdate) => {
    return request.put<NotificationResponse>(`/notifications/${id}`, data)
  },

  // 标记为已读
  markAsRead: (id: number) => {
    return request.post<NotificationResponse>(`/notifications/${id}/read`)
  },

  // 标记所有为已读
  markAllAsRead: () => {
    return request.post('/notifications/mark-all-read')
  },

  // 删除通知
  deleteNotification: (id: number) => {
    return request.delete(`/notifications/${id}`)
  },

  // 获取未读数量
  getUnreadCount: () => {
    return request.get<{ unread_count: number }>('/notifications/unread/count')
  },

  // 获取通知统计
  getStatistics: () => {
    return request.get<NotificationStatistics>('/notifications/statistics/summary')
  },

  // 获取我的通知设置
  getMySettings: () => {
    return request.get<UserNotificationSettings>('/notifications/settings/me')
  },

  // 更新我的通知设置
  updateMySettings: (data: UserNotificationSettingsUpdate) => {
    return request.put<UserNotificationSettings>('/notifications/settings/me', data)
  },

  // 获取通知模板列表
  getTemplates: () => {
    return request.get<NotificationTemplate[]>('/notifications/templates')
  },

  // 使用模板发送通知
  sendFromTemplate: (templateCode: string, recipientId: number, variables: Record<string, any> = {}) => {
    return request.post<NotificationResponse>(
      `/notifications/templates/${templateCode}/send?recipient_id=${recipientId}`,
      variables
    )
  }
}

export default notificationApi
