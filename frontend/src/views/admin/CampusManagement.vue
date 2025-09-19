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
        <el-table-column prop="phone" label="联系电话" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="is_main" label="是否主校区">
          <template #default="scope">
            <el-tag :type="scope.row.is_main ? 'success' : 'info'">
              {{ scope.row.is_main ? '主校区' : '分校区' }}
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
              :disabled="scope.row.is_main"
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
          <el-input v-model="campusForm.name" />
        </el-form-item>
        
        <el-form-item label="地址" prop="address">
          <el-input v-model="campusForm.address" />
        </el-form-item>
        
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="campusForm.contact_person" />
        </el-form-item>
        
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="campusForm.phone" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="campusForm.email" />
        </el-form-item>
        
        <el-form-item label="是否主校区" prop="is_main">
          <el-switch 
            v-model="campusForm.is_main"
            :disabled="isEditMode && campusForm.is_main"
          />
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
import { Plus } from '@element-plus/icons-vue'

const campusFormRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEditMode = ref(false)

const searchForm = reactive({
  name: ''
})

const campusForm = reactive({
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

const campusList = ref([])

const campusRules = {
  name: [
    { required: true, message: '请输入校区名称', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入地址', trigger: 'blur' }
  ],
  contact_person: [
    { required: true, message: '请输入联系人', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
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
    // TODO: 调用获取校区列表API
    console.log('加载校区列表', { 
      page: pagination.page, 
      size: pagination.size,
      ...searchForm 
    })
    
    // 模拟数据
    campusList.value = [
      {
        id: 1,
        name: '总校区',
        address: '北京市朝阳区xxx路123号',
        contact_person: '张主任',
        phone: '13800138001',
        email: 'main@example.com',
        is_main: true
      },
      {
        id: 2,
        name: '海淀分校',
        address: '北京市海淀区xxx路456号',
        contact_person: '李老师',
        phone: '13800138002',
        email: 'haidian@example.com',
        is_main: false
      }
    ]
    pagination.total = 2
  } catch (error) {
    console.error('加载校区列表失败:', error)
    ElMessage.error('加载校区列表失败')
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
  dialogVisible.value = true
}

const showEditDialog = (row: any) => {
  isEditMode.value = true
  Object.assign(campusForm, row)
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
    await campusFormRef.value.validate()
    saving.value = true
    
    // TODO: 调用保存校区API
    console.log('保存校区:', campusForm)
    
    ElMessage.success(isEditMode.value ? '编辑成功' : '新增成功')
    dialogVisible.value = false
    loadCampusList()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个校区吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // TODO: 调用删除校区API
    console.log('删除校区:', row.id)
    
    ElMessage.success('删除成功')
    loadCampusList()
  } catch (error) {
    // 用户取消操作
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
</style>
