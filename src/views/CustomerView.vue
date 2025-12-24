<template>
  <div class="app-container">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="title-icon"><UserFilled /></el-icon>
            <span class="title-text">客户管理 (UC004)</span>
          </div>
          <el-button type="primary" @click="openDialog()">
            <el-icon style="margin-right: 5px"><Plus /></el-icon> 新增客户
          </el-button>
        </div>
      </template>

      <el-table
        :data="tableData"
        border
        stripe
        style="width: 100%"
        :header-cell-style="{background:'#f5f7fa', color:'#606266', fontWeight:'bold'}"
      >
        <el-table-column prop="name" label="客户名称" min-width="150" show-overflow-tooltip>
             <template #default="scope">
                <span style="font-weight: bold; color: #303133">{{ scope.row.name }}</span>
             </template>
        </el-table-column>

        <el-table-column prop="contact" label="联系人" width="120" align="center" />
        <el-table-column prop="phone" label="联系电话" width="140" align="center" />

        <el-table-column prop="default_credit_period" label="默认账期(天)" width="120" align="center">
            <template #default="scope">
                <el-tag v-if="scope.row.default_credit_period > 0" type="success" size="small">{{ scope.row.default_credit_period }} 天</el-tag>
                <span v-else style="color:#ccc">-</span>
            </template>
        </el-table-column>

        <el-table-column prop="address" label="地址" min-width="180" show-overflow-tooltip />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />

        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="scope">
            <el-tooltip content="修改信息" placement="top">
                <el-button type="primary" link :icon="Edit" @click="openDialog(scope.row)"></el-button>
            </el-tooltip>
            <el-tooltip content="删除客户" placement="top">
                <el-button type="danger" link :icon="Delete" @click="handleDelete(scope.row)"></el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="visible" :title="form.id ? '修改客户' : '新增客户'" width="600px" align-center>
      <el-form :model="form" label-width="80px">
        <el-row :gutter="20">
            <el-col :span="12">
                <el-form-item label="名称">
                    <el-input v-model="form.name" placeholder="客户全称" prefix-icon="UserFilled" />
                </el-form-item>
            </el-col>
            <el-col :span="12">
                <el-form-item label="默认账期">
                    <el-input-number v-model="form.default_credit_period" :min="0" style="width: 100%" placeholder="天数"/>
                </el-form-item>
            </el-col>
        </el-row>

        <el-row :gutter="20">
            <el-col :span="12">
                <el-form-item label="联系人">
                    <el-input v-model="form.contact" placeholder="联系人" prefix-icon="User" />
                </el-form-item>
            </el-col>
            <el-col :span="12">
                <el-form-item label="电话">
                    <el-input v-model="form.phone" placeholder="手机/座机" prefix-icon="Phone" />
                </el-form-item>
            </el-col>
        </el-row>

        <el-form-item label="地址">
            <el-input v-model="form.address" placeholder="详细送货地址" prefix-icon="Location" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="其他备注信息"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import axios from 'axios'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Plus, Edit, Delete, UserFilled, User, Phone, Location} from '@element-plus/icons-vue'

const tableData = ref([])
const visible = ref(false)
const form = ref({})

const loadData = async () => {
  try {
    const res = await axios.get('/api/customer')
    tableData.value = res.data.data
  } catch (e) {
    console.error(e)
  }
}

const openDialog = (row = {}) => {
  form.value = { default_credit_period: 0, ...row }
  visible.value = true
}

const handleSubmit = async () => {
  if (!form.value.name) return ElMessage.warning("名称不能为空")

  if (form.value.id) {
    await axios.put('/api/customer', form.value)
    ElMessage.success('修改成功')
  } else {
    await axios.post('/api/customer', form.value)
    ElMessage.success('新增成功')
  }

  visible.value = false
  loadData()
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除客户【${row.name}】吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await axios.delete(`/api/customer?id=${row.id}`)
    ElMessage.success('删除成功')
    loadData()
  })
}

onMounted(loadData)
</script>

<style scoped>
.app-container { width: 100%; }
.main-card { width: 100%; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; }
.title-icon { font-size: 20px; color: #409EFF; margin-right: 8px; background: #ecf5ff; padding: 6px; border-radius: 6px; }
.title-text { font-size: 16px; font-weight: 600; color: #303133; }
:deep(.el-table .el-table__cell.is-fixed-right) { border-left: 1px solid #ebeef5; z-index: 10; }
</style>