// 用户相关类型
export interface User {
  id: number
  username: string
  real_name: string
  gender?: string
  age?: number
  phone: string
  email?: string
  role: UserRole
  campus_id?: number
  avatar_url?: string
  id_number?: string
  is_active: number
  created_at: string
  updated_at?: string
}

export enum UserRole {
  SUPER_ADMIN = 'super_admin',
  CAMPUS_ADMIN = 'campus_admin', 
  COACH = 'coach',
  STUDENT = 'student'
}

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  password: string
  real_name: string
  gender?: string
  age?: number
  phone: string
  email?: string
  campus_id?: number
  avatar_url?: string
  id_number?: string
}

// 校区相关类型
export interface Campus {
  id: number
  name: string
  address: string
  contact_person: string
  contact_phone: string
  contact_email?: string
  admin_id?: number
  is_main_campus: number
  is_active: number
  created_at: string
  updated_at?: string
}

// 教练相关类型
export interface Coach {
  id: number
  user_id: number
  level: CoachLevel
  hourly_rate: number
  achievements?: string
  max_students: number
  current_students: number
  approval_status: string
  approved_by?: number
  approved_at?: string
  created_at: string
  updated_at?: string
}

export enum CoachLevel {
  SENIOR = 'senior',
  INTERMEDIATE = 'intermediate',
  JUNIOR = 'junior'
}

// 学员相关类型
export interface Student {
  id: number
  user_id: number
  account_balance: number
  max_coaches: number
  current_coaches: number
  monthly_cancellations: number
  last_cancellation_reset?: string
  created_at: string
  updated_at?: string
}

// 预约相关类型
export interface Booking {
  id: number
  coach_id: number
  student_id: number
  campus_id: number
  table_number?: string
  start_time: string
  end_time: string
  duration_hours: number
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

// 支付相关类型
export interface Payment {
  id: number
  user_id: number
  amount: number
  payment_method: string
  payment_status: string
  transaction_id?: string
  payment_type: string
  related_id?: number
  qr_code_url?: string
  payment_time?: string
  refund_time?: string
  refund_reason?: string
  notes?: string
  created_by?: number
  created_at: string
  updated_at?: string
}

// 比赛相关类型
export interface Competition {
  id: number
  name: string
  campus_id: number
  competition_date: string
  registration_deadline: string
  registration_fee: number
  max_participants_per_group: number
  status: string
  description?: string
  created_by?: number
  created_at: string
  updated_at?: string
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

// 分页响应类型
export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 表单验证规则类型
export interface FormRule {
  required?: boolean
  message: string
  trigger?: string | string[]
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (rule: any, value: any, callback: any) => void
}
