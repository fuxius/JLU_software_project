<template>
  <div class="admin-layout">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h3>系统管理</h3>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              {{ userStore.user?.real_name || '管理员' }}
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
            <!-- 超级管理员专用菜单 -->
            <el-menu-item 
              v-if="userStore.user?.role === 'super_admin'"
              index="/admin/campus"
            >
              <el-icon><office-building /></el-icon>
              <span>校区管理</span>
            </el-menu-item>
            
            <!-- 超级管理员和校区管理员共用菜单 -->
            <el-menu-item index="/admin/users">
              <el-icon><user /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            
            <el-menu-item index="/admin/competitions">
              <el-icon><trophy /></el-icon>
              <span>比赛管理</span>
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
import { ArrowDown, OfficeBuilding, User, Trophy } from '@element-plus/icons-vue'

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
.admin-layout {
  height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #304156;
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
  background-color: #001529;
}

.sidebar-menu {
  border-right: none;
  background-color: #001529;
}

.sidebar-menu .el-menu-item {
  color: #bfcbd9;
}

.sidebar-menu .el-menu-item:hover {
  background-color: #263445;
  color: #409eff;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #409eff;
  color: white;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
