import request from '@/utils/request'

// 支付相关类型定义
export interface RechargeRequest {
  amount: number
  payment_method: 'wechat' | 'alipay' | 'offline'
  description?: string
}

export interface OfflinePaymentRequest {
  user_id: number
  amount: number
  description?: string
}

export interface PaymentResponse {
  id: number
  user_id: number
  type: string
  amount: number
  payment_method: string
  status: string
  description?: string
  transaction_id?: string
  qr_code_url?: string
  paid_at?: string
  created_at: string
  updated_at?: string
}

export interface BalanceResponse {
  user_id: number
  balance: number
  last_updated: string
}

export interface PaymentSummary {
  total_recharge: number
  total_expense: number
  total_refund: number
  current_balance: number
  payment_count: number
}

export interface RefundRequest {
  amount: number
  reason: string
}

export interface PaymentStatusUpdate {
  status: string
  transaction_id?: string
}

export interface QRCodeResponse {
  qr_code_url: string
}

export interface PaymentQuery {
  payment_type?: string
  skip?: number
  limit?: number
}

// 支付相关API
export const paymentApi = {
  // 创建充值订单
  createRecharge: (data: RechargeRequest) => {
    return request.post<PaymentResponse>('/payments/recharge', data)
  },

  // 生成微信支付二维码
  generateWechatQR: (paymentId: number) => {
    return request.post<QRCodeResponse>(`/payments/wechat-qr/${paymentId}`)
  },

  // 生成支付宝支付二维码
  generateAlipayQR: (paymentId: number) => {
    return request.post<QRCodeResponse>(`/payments/alipay-qr/${paymentId}`)
  },

  // 线下充值录入（管理员）
  createOfflinePayment: (data: OfflinePaymentRequest) => {
    return request.post<PaymentResponse>('/payments/offline', data)
  },

  // 更新支付状态
  updatePaymentStatus: (paymentId: number, data: PaymentStatusUpdate) => {
    return request.put<PaymentResponse>(`/payments/${paymentId}/status`, data)
  },

  // 获取账户余额
  getBalance: () => {
    return request.get<BalanceResponse>('/payments/balance')
  },

  // 获取指定用户余额（管理员）
  getUserBalance: (userId: number) => {
    return request.get<BalanceResponse>(`/payments/balance/${userId}`)
  },

  // 获取支付记录
  getPaymentRecords: (params?: PaymentQuery) => {
    return request.get<PaymentResponse[]>('/payments/records', { params })
  },

  // 获取指定用户支付记录（管理员）
  getUserPaymentRecords: (userId: number, params?: PaymentQuery) => {
    return request.get<PaymentResponse[]>(`/payments/records/${userId}`, { params })
  },

  // 获取所有支付记录（管理员）
  getAllPayments: (params?: { skip?: number; limit?: number }) => {
    return request.get<PaymentResponse[]>('/payments/all', { params })
  },

  // 获取支付汇总
  getPaymentSummary: () => {
    return request.get<PaymentSummary>('/payments/summary')
  },

  // 申请退款（管理员）
  requestRefund: (data: RefundRequest) => {
    return request.post<PaymentResponse>('/payments/refund', data)
  },

  // 快捷充值金额选项
  getQuickRechargeAmounts: () => {
    return [50, 100, 200, 500, 1000, 2000]
  },

  // 格式化金额显示
  formatAmount: (amount: number) => {
    return `¥${amount.toFixed(2)}`
  },

  // 获取支付方式列表
  getPaymentMethods: () => {
    return [
      { value: 'wechat', label: '微信支付', icon: 'wechat' },
      { value: 'alipay', label: '支付宝', icon: 'alipay' },
      { value: 'offline', label: '线下支付', icon: 'cash' }
    ]
  },

  // 获取支付状态文本
  getStatusText: (status: string) => {
    const statusMap: Record<string, string> = {
      'pending': '待支付',
      'success': '支付成功',
      'failed': '支付失败',
      'cancelled': '已取消',
      'refunded': '已退款'
    }
    return statusMap[status] || status
  },

  // 获取支付类型文本
  getTypeText: (type: string) => {
    const typeMap: Record<string, string> = {
      'recharge': '充值',
      'booking': '课程费用',
      'competition': '比赛报名费',
      'refund': '退款'
    }
    return typeMap[type] || type
  }
}
