<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :model="searchForm" inline>
          <el-form-item label="用户名">
            <el-input 
              v-model="searchForm.username" 
              placeholder="请输入用户名"
              clearable
            />
          </el-form-item>
          <el-form-item label="真实姓名">
            <el-input 
              v-model="searchForm.realName" 
              placeholder="请输入真实姓名"
              clearable
            />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="searchForm.role" placeholder="请选择角色" clearable>
              <el-option label="超级管理员" value="super_admin" />
              <el-option label="校区管理员" value="campus_admin" />
              <el-option label="教练" value="coach" />
              <el-option label="学员" value="student" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 用户列表 -->
      <el-table 
        :data="filteredUserList" 
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="real_name" label="真实姓名" />
        <el-table-column prop="role" label="角色">
          <template #default="scope">
            <el-tag :type="getRoleTagType(scope.row.role)">
              {{ getRoleText(scope.row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="scope">
            <span>{{ scope.row.gender === 'male' ? '男' : (scope.row.gender === 'female' ? '女' : '-') }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="is_active" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              v-if="canEditUser(scope.row)"
              type="primary" 
              size="small" 
              @click="showEditDialog(scope.row)"
            >
              编辑
            </el-button>
            <el-button 
              v-if="canToggleUserStatus(scope.row)"
              :type="scope.row.is_active ? 'warning' : 'success'"
              size="small" 
              @click="toggleUserStatus(scope.row)"
            >
              {{ scope.row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              v-if="canResetPassword(scope.row)"
              type="info" 
              size="small" 
              @click="resetPassword(scope.row)"
            >
              重置密码
            </el-button>
            <el-tag v-if="!canEditUser(scope.row)" type="info" size="small">
              无权限操作
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 编辑用户对话框 -->
    <el-dialog
      title="编辑用户"
      v-model="dialogVisible"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="100px"
      >
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" disabled />
        </el-form-item>
        
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="userForm.real_name" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option 
              v-for="role in availableRoles"
              :key="role.value"
              :label="role.label"
              :value="role.value"
              :disabled="!canSetRole(role.value)"
            />
          </el-select>
          <div v-if="isCampusAdmin" class="role-tip">
            <el-text type="info" size="small">
              注：校区管理员无权设置校区管理员及以上级别的角色
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="userForm.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="userForm.age" :min="1" :max="120" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="saving">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { usersApi } from '../../api/users'
import { useUserStore } from '@/store/user'
import type { User } from '../../types'

const userFormRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const userStore = useUserStore()

// 权限控制相关的计算属性
const currentUserRole = computed(() => userStore.userRole)
const isSuperAdmin = computed(() => userStore.isSuperAdmin)
const isCampusAdmin = computed(() => userStore.isCampusAdmin)

// 角色权限等级定义（数字越大权限越高）
const roleLevel = computed(() => {
  const levels: Record<string, number> = {
    'student': 1,
    'coach': 2,
    'campus_admin': 3,
    'super_admin': 4
  }
  return levels
})

// 当前用户的权限等级
const currentUserLevel = computed(() => {
  return roleLevel.value[currentUserRole.value || ''] || 0
})

// 过滤用户列表 - 校区管理员不能看到超级管理员
const filteredUserList = computed(() => {
  if (isSuperAdmin.value) {
    // 超级管理员可以看到所有用户
    return userList.value
  } else if (isCampusAdmin.value) {
    // 校区管理员不能看到超级管理员
    return userList.value.filter(user => user.role !== 'super_admin')
  }
  return userList.value
})

// 可选择的角色列表 - 根据当前用户权限过滤
const availableRoles = computed(() => {
  const allRoles = [
    { label: '超级管理员', value: 'super_admin' },
    { label: '校区管理员', value: 'campus_admin' },
    { label: '教练', value: 'coach' },
    { label: '学员', value: 'student' }
  ]
  
  if (isSuperAdmin.value) {
    // 超级管理员可以设置所有角色
    return allRoles
  } else if (isCampusAdmin.value) {
    // 校区管理员不能设置校区管理员及以上级别的角色
    return allRoles.filter(role => 
      roleLevel.value[role.value] < roleLevel.value['campus_admin']
    )
  }
  
  return allRoles.filter(role => role.value === 'student') // 默认只能设置学员
})

// 检查是否可以编辑某个用户
const canEditUser = (user: User) => {
  if (isSuperAdmin.value) {
    return true // 超级管理员可以编辑所有用户
  } else if (isCampusAdmin.value) {
    // 校区管理员不能编辑超级管理员
    return user.role !== 'super_admin'
  }
  return false // 其他角色不能编辑用户
};

// 检查是否可以禁用/启用某个用户
const canToggleUserStatus = (user: User) => {
  return canEditUser(user) // 与编辑权限相同
};

// 检查是否可以重置某个用户的密码
const canResetPassword = (user: User) => {
  return canEditUser(user) // 与编辑权限相同
};

// 检查是否可以设置某个角色
const canSetRole = (roleValue: string) => {
  if (isSuperAdmin.value) {
    return true // 超级管理员可以设置任何角色
  } else if (isCampusAdmin.value) {
    // 校区管理员不能设置校区管理员及以上级别的角色
    return roleLevel.value[roleValue] < roleLevel.value['campus_admin']
  }
  return false
};

const searchForm = reactive({
  username: '',
  realName: '',
  role: ''
})

const userForm = reactive<{
  id: number | null
  username: string
  real_name: string
  role: string
  phone: string
  email: string
  gender: string
  age: number
}>({
  id: null,
  username: '',
  real_name: '',
  role: '',
  phone: '',
  email: '',
  gender: 'male',
  age: 18
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const userList = ref<User[]>([])

const userRules = {
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const getRoleText = (role: string) => {
  const roleMap: Record<string, string> = {
    'super_admin': '超级管理员',
    'campus_admin': '校区管理员',
    'coach': '教练',
    'student': '学员'
  }
  return roleMap[role] || role
}

const getRoleTagType = (role: string) => {
  const typeMap: Record<string, string> = {
    'super_admin': 'danger',
    'campus_admin': 'warning',
    'coach': 'success',
    'student': 'info'
  }
  return typeMap[role] || 'info'
}

const loadUserList = async () => {
  loading.value = true
  try {
    const response = await usersApi.getUsersList({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      username: searchForm.username || undefined,
      real_name: searchForm.realName || undefined,
      role: searchForm.role || undefined
    })
    
    // 处理可能的响应格式
    const data = response.data || response
    userList.value = data.items || data
    pagination.total = data.total || userList.value.length
  } catch (error: any) {
    console.error('加载用户列表失败:', error)
    ElMessage.error(error?.response?.data?.detail || '加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadUserList()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    username: '',
    realName: '',
    role: ''
  })
  handleSearch()
}

const showEditDialog = (row: User) => {
  // 检查是否有编辑权限
  if (!canEditUser(row)) {
    ElMessage.warning('您没有权限编辑此用户')
    return
  }
  
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    real_name: row.real_name,
    role: row.role,
    phone: row.phone,
    email: row.email || '',
    gender: row.gender || 'male',
    age: row.age || 18
  })
  dialogVisible.value = true
}

const resetForm = () => {
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
  Object.assign(userForm, {
    id: null,
    username: '',
    real_name: '',
    role: '',
    phone: '',
    email: '',
    gender: 'male',
    age: 18
  })
}

const handleSave = async () => {
  if (!userFormRef.value || !userForm.id) return
  
  try {
    await userFormRef.value.validate()
    saving.value = true
    
    await usersApi.updateUser(userForm.id, {
      real_name: userForm.real_name,
      role: userForm.role,
      phone: userForm.phone,
      email: userForm.email,
      gender: userForm.gender,
      age: userForm.age
    })
    
    ElMessage.success('更新成功')
    dialogVisible.value = false
    loadUserList()
  } catch (error: any) {
    console.error('更新失败:', error)
    ElMessage.error(error?.response?.data?.detail || '更新失败')
  } finally {
    saving.value = false
  }
}

const toggleUserStatus = async (row: User) => {
  // 检查权限
  if (!canToggleUserStatus(row)) {
    ElMessage.warning('您没有权限操作此用户')
    return
  }
  
  const action = row.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 ${row.username} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await usersApi.toggleUserStatus(row.id)
    
    ElMessage.success(`${action}成功`)
    loadUserList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error(`${action}用户失败:`, error)
      ElMessage.error(error?.response?.data?.detail || `${action}用户失败`)
    }
  }
}

const resetPassword = async (row: User) => {
  // 检查权限
  if (!canResetPassword(row)) {
    ElMessage.warning('您没有权限重置此用户的密码')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要重置用户 ${row.username} 的密码吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await usersApi.resetUserPassword(row.id)
    
    // 显示新密码给管理员
    const newPassword = response.data?.new_password
    if (newPassword) {
      await ElMessageBox.alert(`密码重置成功！新密码是：${newPassword}`, '密码重置成功', {
        confirmButtonText: '确定',
        type: 'success'
      })
    } else {
      ElMessage.success('密码重置成功')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('重置密码失败:', error)
      ElMessage.error(error?.response?.data?.detail || '重置密码失败')
    }
  }
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  loadUserList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadUserList()
}

onMounted(() => {
  loadUserList()
})
</script>

<style scoped>
.user-management {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.dialog-footer {
  text-align: right;
}

.role-tip {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}
</style>
