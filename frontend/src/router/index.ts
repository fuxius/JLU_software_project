import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { 
      title: '登录',
      requiresAuth: false 
    }
  },
  {
    path: '/register',
    name: 'Register', 
    component: () => import('@/views/auth/Register.vue'),
    meta: { 
      title: '注册',
      requiresAuth: false 
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { 
      title: '仪表板',
      requiresAuth: true 
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/user/Profile.vue'),
    meta: { 
      title: '个人信息',
      requiresAuth: true 
    }
  },
  // 超级管理员路由
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/admin/Layout.vue'),
    meta: { 
      title: '系统管理',
      requiresAuth: true,
      roles: ['super_admin']
    },
    children: [
      {
        path: 'campus',
        name: 'CampusManagement',
        component: () => import('@/views/admin/CampusManagement.vue'),
        meta: { 
          title: '校区管理',
          requiresAuth: true,
          roles: ['super_admin']
        }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: { 
          title: '用户管理',
          requiresAuth: true,
          roles: ['super_admin', 'campus_admin']
        }
      }
    ]
  },
  // 学员路由
  {
    path: '/student',
    name: 'Student',
    component: () => import('@/views/student/Layout.vue'),
    meta: { 
      title: '学员中心',
      requiresAuth: true,
      roles: ['student']
    },
    children: [
      {
        path: 'coaches',
        name: 'CoachList',
        component: () => import('@/views/student/CoachList.vue'),
        meta: { 
          title: '教练列表',
          requiresAuth: true,
          roles: ['student']
        }
      },
      {
        path: 'bookings',
        name: 'StudentBookings',
        component: () => import('@/views/student/Bookings.vue'),
        meta: { 
          title: '我的预约',
          requiresAuth: true,
          roles: ['student']
        }
      },
      {
        path: 'payments',
        name: 'StudentPayments',
        component: () => import('@/views/student/Payments.vue'),
        meta: { 
          title: '账户充值',
          requiresAuth: true,
          roles: ['student']
        }
      },
      {
        path: 'booking',
        name: 'StudentBooking',
        component: () => import('@/views/student/Booking.vue'),
        meta: {
          title: '预约教练',
          requiresAuth: true,
          roles: ['student']
        }
      },
      {
        path: 'competitions',
        name: 'StudentCompetitions',
        component: () => import('@/views/student/Competitions.vue'),
        meta: {
          title: '比赛报名',
          requiresAuth: true,
          roles: ['student']
        }
      }
    ]
  },
  // 教练路由
  {
    path: '/coach',
    name: 'Coach',
    component: () => import('@/views/coach/Layout.vue'),
    meta: { 
      title: '教练中心',
      requiresAuth: true,
      roles: ['coach']
    },
    children: [
      {
        path: 'students',
        name: 'CoachStudents',
        component: () => import('@/views/coach/Students.vue'),
        meta: { 
          title: '我的学员',
          requiresAuth: true,
          roles: ['coach']
        }
      },
      {
        path: 'bookings',
        name: 'CoachBookings',
        component: () => import('@/views/coach/Bookings.vue'),
        meta: { 
          title: '课程安排',
          requiresAuth: true,
          roles: ['coach']
        }
      },
      {
        path: 'evaluations',
        name: 'CoachEvaluations',
        component: () => import('@/views/coach/Evaluations.vue'),
        meta: { 
          title: '课后评价',
          requiresAuth: true,
          roles: ['coach']
        }
      }
    ]
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFound.vue'),
    meta: { 
      title: '页面不存在',
      requiresAuth: false 
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 乒乓球培训管理系统`
  }
  
  // 检查是否需要认证
  if (to.meta?.requiresAuth) {
    if (!userStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      next('/login')
      return
    }
    
    // 检查角色权限
    if (to.meta?.roles) {
      const userRole = userStore.userRole
      if (!userRole || !to.meta.roles.includes(userRole)) {
        ElMessage.error('权限不足')
        next('/dashboard')
        return
      }
    }
  }
  
  // 如果已登录，不允许访问登录/注册页面
  if ((to.path === '/login' || to.path === '/register') && userStore.isLoggedIn) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router
