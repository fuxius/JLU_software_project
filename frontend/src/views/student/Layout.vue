<template>
  <div class="student-layout">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h3>学员中心</h3>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              {{ userStore.user?.real_name || '学员' }}
              <el-icon><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-container>
        <el-aside class="sidebar">
          <el-menu
            :default-active="$route.path"
            class="sidebar-menu"
            router
            unique-opened
          >
            <el-menu-item index="/student/messages">
              <el-icon><bell /></el-icon>
              <span>消息</span>
            </el-menu-item>
            <el-menu-item index="/student/coaches">
              <el-icon><user /></el-icon>
              <span>教练列表</span>
            </el-menu-item>
            <el-menu-item index="/student/bookings">
              <el-icon><calendar /></el-icon>
              <span>我的预约</span>
            </el-menu-item>
            <el-menu-item index="/student/payments">
              <el-icon><wallet /></el-icon>
              <span>账户充值</span>
            </el-menu-item>
            <el-menu-item index="/student/competitions">
              <el-icon><trophy /></el-icon>
              <span>比赛报名</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, User, Calendar, Wallet, Trophy, Bell } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await userStore.logout()
        ElMessage.success('退出登录成功')
        router.push('/login')
      } catch (error) {
        // 用户取消操作
      }
      break
  }
}
</script>

<style scoped>
.student-layout {
  height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #409eff;
  color: white;
  padding: 0 20px;
}

.header-left h3 {
  margin: 0;
  color: white;
}

.header-right {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
}

.sidebar {
  width: 200px;
  background-color: #f0f2f5;
}

.sidebar-menu {
  border-right: none;
  background-color: #f0f2f5;
}

.main-content {
  background-color: #ffffff;
  padding: 20px;
}
</style>