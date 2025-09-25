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
        :data="userList" 
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
            <span>{{ scope.row.gender === 'male' ? '男' : scope.row.gender === 'female' ? '女' : '-' }}</span>
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
              type="primary" 
              size="small" 
              @click="showEditDialog(scope.row)"
            >
              编辑
            </el-button>
            <el-button 
              :type="scope.row.is_active ? 'warning' : 'success'"
              size="small" 
              @click="toggleUserStatus(scope.row)"
            >
              {{ scope.row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="resetPassword(scope.row)"
            >
              重置密码
            </el-button>
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
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="校区管理员" value="campus_admin" />
            <el-option label="教练" value="coach" />
            <el-option label="学员" value="student" />
          </el-select>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { usersApi } from '../../api/users'
import type { User } from '../../types'

const userFormRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)

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
    
    userList.value = response.items
    pagination.total = response.total
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
</style>
