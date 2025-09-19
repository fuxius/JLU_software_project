<template>
  <div class="dashboard-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="250px">
        <div class="sidebar">
          <div class="logo">
            <h2>乒乓球培训系统</h2>
          </div>
          
          <el-menu
            :default-active="activeMenu"
            class="sidebar-menu"
            @select="handleMenuSelect"
          >
            <!-- 通用菜单 -->
            <el-menu-item index="/dashboard">
              <el-icon><House /></el-icon>
              <span>仪表板</span>
            </el-menu-item>
            
            <el-menu-item index="/profile">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </el-menu-item>
            
            <!-- 超级管理员菜单 -->
            <template v-if="userStore.isSuperAdmin">
              <el-sub-menu index="admin">
                <template #title>
                  <el-icon><Setting /></el-icon>
                  <span>系统管理</span>
                </template>
                <el-menu-item index="/admin/campus">校区管理</el-menu-item>
                <el-menu-item index="/admin/users">用户管理</el-menu-item>
              </el-sub-menu>
            </template>
            
            <!-- 校区管理员菜单 -->
            <template v-if="userStore.isCampusAdmin">
              <el-menu-item index="/admin/users">
                <el-icon><UserFilled /></el-icon>
                <span>用户管理</span>
              </el-menu-item>
            </template>
            
            <!-- 学员菜单 -->
            <template v-if="userStore.isStudent">
              <el-menu-item index="/student/coaches">
                <el-icon><Avatar /></el-icon>
                <span>教练列表</span>
              </el-menu-item>
              <el-menu-item index="/student/bookings">
                <el-icon><Calendar /></el-icon>
                <span>我的预约</span>
              </el-menu-item>
              <el-menu-item index="/student/payments">
                <el-icon><CreditCard /></el-icon>
                <span>账户充值</span>
              </el-menu-item>
              <el-menu-item index="/student/competitions">
                <el-icon><Trophy /></el-icon>
                <span>比赛报名</span>
              </el-menu-item>
            </template>
            
            <!-- 教练菜单 -->
            <template v-if="userStore.isCoach">
              <el-menu-item index="/coach/students">
                <el-icon><UserFilled /></el-icon>
                <span>我的学员</span>
              </el-menu-item>
              <el-menu-item index="/coach/bookings">
                <el-icon><Calendar /></el-icon>
                <span>课程安排</span>
              </el-menu-item>
              <el-menu-item index="/coach/evaluations">
                <el-icon><Document /></el-icon>
                <span>课后评价</span>
              </el-menu-item>
            </template>
          </el-menu>
        </div>
      </el-aside>
      
      <!-- 主内容区域 -->
      <el-container>
        <!-- 头部 -->
        <el-header class="header">
          <div class="header-content">
            <div class="header-left">
              <h3>{{ pageTitle }}</h3>
            </div>
            <div class="header-right">
              <el-dropdown @command="handleCommand">
                <div class="user-info">
                  <el-avatar :size="32" :src="userStore.user?.avatar_url">
                    {{ userStore.user?.real_name?.charAt(0) }}
                  </el-avatar>
                  <span class="username">{{ userStore.user?.real_name }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                    <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                    <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        
        <!-- 主体内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 修改密码对话框 -->
    <el-dialog v-model="changePasswordVisible" title="修改密码" width="400px">
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="原密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changePasswordVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">
          确认
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElForm, ElMessageBox } from 'element-plus'
import {
  House, User, Setting, UserFilled, Avatar, Calendar,
  CreditCard, Trophy, Document, ArrowDown
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const passwordFormRef = ref<InstanceType<typeof ElForm>>()
const changePasswordVisible = ref(false)
const passwordLoading = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 页面标题
const pageTitle = computed(() => {
  return route.meta?.title || '仪表板'
})

// 修改密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码验证规则
const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, max: 16, message: '密码长度为8-16位', trigger: 'blur' },
    {
      pattern: /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?])/,
      message: '密码必须包含字母、数字和特殊字符',
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: any, callback: any) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 菜单选择处理
const handleMenuSelect = (index: string) => {
  router.push(index)
}

// 下拉菜单命令处理
const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'changePassword':
      changePasswordVisible.value = true
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true
    
    await userStore.changePassword(passwordForm.oldPassword, passwordForm.newPassword)
    changePasswordVisible.value = false
    
    // 重置表单
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    passwordLoading.value = false
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    userStore.logout()
  } catch (error) {
    // 用户取消
  }
}
</script>

<style scoped lang="scss">
.dashboard-container {
  height: 100vh;
  
  .el-container {
    height: 100%;
  }
}

.sidebar {
  height: 100%;
  background-color: #304156;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #2b3a4b;
    
    h2 {
      color: white;
      font-size: 16px;
      font-weight: 600;
      margin: 0;
    }
  }
  
  .sidebar-menu {
    border: none;
    background-color: #304156;
    
    :deep(.el-menu-item) {
      color: #bfcbd9;
      
      &:hover,
      &.is-active {
        background-color: #263445 !important;
        color: #409eff;
      }
    }
    
    :deep(.el-sub-menu__title) {
      color: #bfcbd9;
      
      &:hover {
        background-color: #263445 !important;
        color: #409eff;
      }
    }
  }
}

.header {
  background-color: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  
  .header-content {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    
    .header-left {
      h3 {
        margin: 0;
        color: #303133;
        font-weight: 500;
      }
    }
    
    .header-right {
      .user-info {
        display: flex;
        align-items: center;
        cursor: pointer;
        padding: 8px 12px;
        border-radius: 6px;
        transition: background-color 0.3s;
        
        &:hover {
          background-color: #f5f7fa;
        }
        
        .username {
          margin: 0 8px;
          color: #606266;
          font-size: 14px;
        }
        
        .el-icon {
          color: #909399;
          font-size: 12px;
        }
      }
    }
  }
}

.main-content {
  background-color: #f5f5f5;
  padding: 20px;
}
</style>
