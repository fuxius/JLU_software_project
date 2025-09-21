/**
 * 比赛管理相关API
 */
import request from '@/utils/request'

// 比赛状态枚举
export enum CompetitionStatus {
  UPCOMING = 'upcoming',      // 即将开始
  REGISTRATION = 'registration',  // 报名中
  DRAW_COMPLETE = 'draw_complete',  // 抽签完成
  IN_PROGRESS = 'in_progress',  // 进行中
  COMPLETED = 'completed',    // 已结束
  CANCELLED = 'cancelled'     // 已取消
}

// 比赛组别枚举
export enum CompetitionGroup {
  GROUP_A = 'A',  // 甲组
  GROUP_B = 'B',  // 乙组
  GROUP_C = 'C'   // 丙组
}

// 基础比赛信息
export interface CompetitionBase {
  title: string
  description?: string
  competition_date: string
  registration_deadline: string
  registration_fee: number
  max_participants: number
  campus_id: number
}

// 创建比赛
export interface CompetitionCreate extends CompetitionBase {}

// 更新比赛
export interface CompetitionUpdate {
  title?: string
  description?: string
  competition_date?: string
  registration_deadline?: string
  registration_fee?: number
  max_participants?: number
  status?: string
}

// 比赛响应
export interface CompetitionResponse extends CompetitionBase {
  id: number
  status: string
  created_at: string
  updated_at?: string
  registered_count: number
}

// 比赛查询参数
export interface CompetitionQuery {
  status?: string
  campus_id?: number
  start_date?: string
  end_date?: string
  page?: number
  size?: number
}

// 比赛报名
export interface CompetitionRegistrationCreate {
  competition_id: number
  group_type: string
}

// 比赛报名响应
export interface CompetitionRegistrationResponse extends CompetitionRegistrationCreate {
  id: number
  student_id: number
  payment_id?: number
  is_confirmed: boolean
  created_at: string
  student?: any
}

// 比赛对阵
export interface CompetitionMatch {
  id: number
  competition_id: number
  group_type: string
  round_number: number
  match_number: number
  player1_id?: number
  player2_id?: number
  player1_score?: number
  player2_score?: number
  winner_id?: number
  match_status: string
  scheduled_time?: string
  actual_start_time?: string
  actual_end_time?: string
  table_id?: number
  referee_notes?: string
  created_at: string
  updated_at?: string
  player1?: any
  player2?: any
  winner?: any
}

// 比赛对阵更新
export interface CompetitionMatchUpdate {
  player1_score?: number
  player2_score?: number
  winner_id?: number
  match_status?: string
  actual_start_time?: string
  actual_end_time?: string
  referee_notes?: string
}

// 抽签请求
export interface DrawRequest {
  competition_id: number
  group_type: string
}

// 比赛统计
export interface CompetitionStatistics {
  total_competitions: number
  upcoming_competitions: number
  ongoing_competitions: number
  completed_competitions: number
  total_participants: number
  popular_groups: Array<{
    group: string
    count: number
  }>
}

export const competitionApi = {
  // 创建比赛
  createCompetition: (data: CompetitionCreate) => {
    return request.post<CompetitionResponse>('/competitions', data)
  },

  // 获取比赛列表
  getCompetitions: (params?: CompetitionQuery) => {
    return request.get<CompetitionResponse[]>('/competitions', { params })
  },

  // 获取比赛详情
  getCompetition: (id: number) => {
    return request.get<CompetitionResponse>(`/competitions/${id}`)
  },

  // 更新比赛信息
  updateCompetition: (id: number, data: CompetitionUpdate) => {
    return request.put<CompetitionResponse>(`/competitions/${id}`, data)
  },

  // 报名比赛
  registerCompetition: (competitionId: number, groupType: string) => {
    return request.post<CompetitionRegistrationResponse>(
      `/competitions/${competitionId}/register?group_type=${groupType}`
    )
  },

  // 获取报名列表
  getRegistrations: (competitionId: number, groupType?: string) => {
    const params: any = {}
    if (groupType) params.group_type = groupType
    return request.get<CompetitionRegistrationResponse[]>(
      `/competitions/${competitionId}/registrations`,
      { params }
    )
  },

  // 确认报名
  confirmRegistration: (registrationId: number) => {
    return request.post<CompetitionRegistrationResponse>(
      `/competitions/registrations/${registrationId}/confirm`
    )
  },

  // 生成对阵
  generateDraw: (competitionId: number, groupType: string) => {
    return request.post<CompetitionMatch[]>(
      `/competitions/${competitionId}/draw?group_type=${groupType}`
    )
  },

  // 获取对阵列表
  getMatches: (competitionId: number, groupType?: string) => {
    const params: any = {}
    if (groupType) params.group_type = groupType
    return request.get<CompetitionMatch[]>(
      `/competitions/${competitionId}/matches`,
      { params }
    )
  },

  // 更新比赛结果
  updateMatchResult: (matchId: number, data: CompetitionMatchUpdate) => {
    return request.put<CompetitionMatch>(`/competitions/matches/${matchId}`, data)
  },

  // 获取比赛统计
  getStatistics: () => {
    return request.get<CompetitionStatistics>('/competitions/statistics/summary')
  }
}

export default competitionApi
