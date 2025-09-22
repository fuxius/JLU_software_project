import request from '@/utils/request'

// 预约相关类型定义
export interface BookingCreate {
  coach_id: number
  student_id: number
  campus_id: number
  start_time: string
  end_time: string
  duration_hours: number
  booking_message?: string
  table_number?: string
}

export interface BookingResponse {
  id: number
  coach_id: number
  student_id: number
  campus_id: number
  start_time: string
  end_time: string
  duration_hours: number
  table_number?: string
  hourly_rate: number
  total_cost: number
  status: string
  booking_message?: string
  response_message?: string
  cancelled_by?: number
  cancelled_at?: string
  cancellation_reason?: string
  cancel_confirmed_by?: number
  cancel_confirmed_at?: string
  created_at: string
  updated_at?: string
}

export interface BookingQuery {
  status?: string
  coach_id?: number
  student_id?: number
  campus_id?: number
  start_date?: string
  end_date?: string
  skip?: number
  limit?: number
}

export interface ScheduleQuery {
  coach_id: number
  date_from: string
  date_to: string
}

export interface CourtQuery {
  campus_id: number
  start_time: string
  end_time: string
}

export interface BookingConfirmation {
  action: 'confirm' | 'reject'
  message?: string
}

export interface BookingCancellation {
  cancellation_reason: string
}

export interface ScheduleItem {
  id: number
  start_time: string
  end_time: string
  table_number?: string
  status: string
  student_name?: string
}

// 预约相关API
export const bookingApi = {
  // 创建预约
  createBooking: (data: BookingCreate) => {
    return request.post<BookingResponse>('/bookings', data)
  },

  // 获取预约列表
  getBookings: (params?: BookingQuery) => {
    return request.get<BookingResponse[]>('/bookings', { params })
  },

  // 获取预约详情
  getBooking: (id: number) => {
    return request.get<BookingResponse>(`/bookings/${id}`)
  },

  // 确认/拒绝预约
  confirmBooking: (id: number, data: BookingConfirmation) => {
    return request.put<BookingResponse>(`/bookings/${id}/confirm`, data)
  },

  // 取消预约
  cancelBooking: (id: number, data: BookingCancellation) => {
    return request.put<BookingResponse>(`/bookings/${id}/cancel`, data)
  },

  // 获取教练课表
  getCoachSchedule: (params: ScheduleQuery) => {
    return request.get<ScheduleItem[]>('/bookings/schedule', { params })
  },

  // 获取可用球台
  getAvailableCourts: (params: CourtQuery) => {
    return request.get<string[]>('/bookings/available-courts', { params })
  },

  // 获取我的预约（学员）
  getMyBookings: (params?: { status?: string; skip?: number; limit?: number }) => {
    return request.get<BookingResponse[]>('/bookings/my', { params })
  },

  // 获取待确认预约（教练）
  getPendingBookings: (params?: { skip?: number; limit?: number }) => {
    return request.get<BookingResponse[]>('/bookings/pending', { params })
  },

  // 获取今日课程
  getTodayBookings: () => {
    return request.get<BookingResponse[]>('/bookings/today')
  },

  // 获取本周课程
  getWeekBookings: () => {
    return request.get<BookingResponse[]>('/bookings/week')
  }
}
