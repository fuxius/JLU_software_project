<template>
  <div class="campus-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>校区管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><plus /></el-icon>
            新增校区
          </el-button>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :model="searchForm" inline>
          <el-form-item label="校区名称">
            <el-input 
              v-model="searchForm.name" 
              placeholder="请输入校区名称"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 校区列表 -->
      <el-table 
        :data="campusList" 
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="校区名称" />
        <el-table-column prop="address" label="地址" />
        <el-table-column prop="contact_person" label="联系人" />
        <el-table-column prop="contact_phone" label="联系电话" />
        <el-table-column prop="contact_email" label="邮箱" />
        <el-table-column prop="is_main_campus" label="是否主校区">
          <template #default="scope">
            <el-tag :type="scope.row.is_main_campus ? 'success' : 'info'">
              {{ scope.row.is_main_campus ? '主校区' : '分校区' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="showEditDialog(scope.row)"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
              :disabled="scope.row.is_main_campus"
            >
              删除
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
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="campusFormRef"
        :model="campusForm"
        :rules="campusRules"
        label-width="100px"
      >
        <el-form-item label="校区名称" prop="name">
          <el-input 
            v-model="campusForm.name" 
            placeholder="请输入校区名称，如：北京主校区"
            maxlength="50"
            show-word-limit
          >
            <template #append>
              <el-button @click="fillDemoData" size="small" text>
                填充示例
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="地址" prop="address">
          <el-input 
            v-model="campusForm.address" 
            type="textarea"
            :rows="2"
            placeholder="请输入校区详细地址"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="联系人" prop="contact_person">
          <el-input 
            v-model="campusForm.contact_person" 
            placeholder="请输入联系人姓名"
            maxlength="20"
          />
        </el-form-item>
        
        <el-form-item label="联系电话" prop="phone">
          <el-input 
            v-model="campusForm.phone" 
            placeholder="请输入11位手机号"
            maxlength="11"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="campusForm.email" 
            placeholder="请输入邮箱地址"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="是否主校区" prop="is_main">
          <el-switch 
            v-model="campusForm.is_main"
            :disabled="isEditMode && campusForm.is_main"
            active-text="主校区"
            inactive-text="分校区"
          />
          <div class="form-tip" v-if="campusForm.is_main">
            <el-text type="warning" size="small">
              <el-icon><warning /></el-icon>
              设置为主校区将取消其他校区的主校区标识
            </el-text>
          </div>
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
import { Plus, Warning } from '@element-plus/icons-vue'
import { campusApi } from '../../api/campus'
import type { Campus } from '../../types'

const campusFormRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEditMode = ref(false)

const searchForm = reactive({
  name: ''
})

const campusForm = reactive<{
  id: number | null
  name: string
  address: string
  contact_person: string
  phone: string
  email: string
  is_main: boolean
}>({
  id: null,
  name: '',
  address: '',
  contact_person: '',
  phone: '',
  email: '',
  is_main: false
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const campusList = ref<Campus[]>([])

const campusRules = {
  name: [
    { required: true, message: '请输入校区名称', trigger: 'blur' },
    { min: 2, max: 50, message: '校区名称长度在2到50个字符', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入地址', trigger: 'blur' },
    { min: 5, max: 200, message: '地址长度在5到200个字符', trigger: 'blur' }
  ],
  contact_person: [
    { required: true, message: '请输入联系人', trigger: 'blur' },
    { min: 2, max: 20, message: '联系人姓名长度在2到20个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => isEditMode.value ? '编辑校区' : '新增校区')

const loadCampusList = async () => {
  loading.value = true
  try {
    const response = await campusApi.getCampuses({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      name: searchForm.name || undefined
    })
    
    // 修复响应数据访问
    const data = response.data || response
    campusList.value = data.items || data
    pagination.total = data.total || (Array.isArray(data) ? data.length : 0)
  } catch (error: any) {
    console.error('加载校区列表失败:', error)
    ElMessage.error(error?.response?.data?.detail || '加载校区列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadCampusList()
}

const resetSearch = () => {
  searchForm.name = ''
  handleSearch()
}

const showAddDialog = () => {
  isEditMode.value = false
  resetForm() // 确保表单数据被清空
  
  // 检查是否已有主校区，如果没有则建议设置为主校区
  const hasMainCampus = campusList.value.some(campus => campus.is_main_campus)
  if (!hasMainCampus && campusList.value.length === 0) {
    campusForm.is_main = true // 如果是第一个校区，默认设为主校区
    ElMessage.info('建议将第一个校区设置为主校区')
  }
  
  dialogVisible.value = true
}

// 填充示例数据，方便测试
const fillDemoData = () => {
  const demoData = [
    {
      name: '北京主校区',
      address: '北京市海淀区中关村大街123号',
      contact_person: '张经理',
      phone: '13800138001',
      email: 'beijing@example.com',
      is_main: true
    },
    {
      name: '上海分校区',
      address: '上海市浦东新区世纪大道456号',
      contact_person: '李经理',
      phone: '13800138002',
      email: 'shanghai@example.com',
      is_main: false
    },
    {
      name: '深圳分校区',
      address: '深圳市南山区科技园789号',
      contact_person: '王经理',
      phone: '13800138003',
      email: 'shenzhen@example.com',
      is_main: false
    }
  ]
  
  const randomDemo = demoData[Math.floor(Math.random() * demoData.length)]
  Object.assign(campusForm, randomDemo)
  ElMessage.success('已填充示例数据，请根据需要修改')
}

const showEditDialog = (row: Campus) => {
  isEditMode.value = true
  Object.assign(campusForm, {
    id: row.id,
    name: row.name,
    address: row.address,
    contact_person: row.contact_person,
    phone: row.contact_phone,
    email: row.contact_email || '',
    is_main: row.is_main_campus === 1
  })
  dialogVisible.value = true
}

const resetForm = () => {
  if (campusFormRef.value) {
    campusFormRef.value.resetFields()
  }
  Object.assign(campusForm, {
    id: null,
    name: '',
    address: '',
    contact_person: '',
    phone: '',
    email: '',
    is_main: false
  })
}

const handleSave = async () => {
  if (!campusFormRef.value) return
  
  try {
    // 表单验证
    await campusFormRef.value.validate()
    saving.value = true
    
    // 准备数据
    const campusData = {
      name: campusForm.name.trim(),
      address: campusForm.address.trim(),
      contact_person: campusForm.contact_person.trim(),
      contact_phone: campusForm.phone.trim(),
      contact_email: campusForm.email.trim(),
      is_main_campus: campusForm.is_main
    }
    
    let response
    if (isEditMode.value && campusForm.id) {
      response = await campusApi.updateCampus(campusForm.id, campusData)
      ElMessage.success('校区信息更新成功！')
    } else {
      response = await campusApi.createCampus(campusData)
      ElMessage.success('校区创建成功！')
    }
    
    dialogVisible.value = false
    // 重新加载数据，如果是新增则回到第一页
    if (!isEditMode.value) {
      pagination.page = 1
    }
    await loadCampusList()
    
  } catch (error: any) {
    console.error('保存失败:', error)
    
    // 处理不同类型的错误
    let errorMessage = '保存失败'
    if (error?.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error?.response?.status === 400) {
      errorMessage = '数据格式错误，请检查输入内容'
    } else if (error?.response?.status === 409) {
      errorMessage = '校区名称已存在，请使用其他名称'
    } else if (error?.message) {
      errorMessage = error.message
    }
    
    ElMessage.error(errorMessage)
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row: Campus) => {
  try {
    await ElMessageBox.confirm('确定要删除这个校区吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await campusApi.deleteCampus(row.id)
    ElMessage.success('删除成功')
    loadCampusList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error?.response?.data?.detail || '删除失败')
    }
  }
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  loadCampusList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadCampusList()
}

onMounted(() => {
  loadCampusList()
})
</script>

<style scoped>
.campus-management {
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

.form-tip {
  margin-top: 8px;
}

.form-tip .el-text {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
