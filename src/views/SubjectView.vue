<template>
  <div class="app-container">
    <el-card class="subject-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="title-icon"><Collection /></el-icon>
            <span class="title-text">会计科目设置 (UC006)</span>
          </div>
          <div>
            <el-button type="warning" plain @click="handleInit">
              <el-icon style="margin-right:5px"><MagicStick /></el-icon> 一键生成默认科目
            </el-button>
            <el-button type="primary" @click="openAddDialog(null)">
              <el-icon style="margin-right:5px"><Plus /></el-icon> 新增一级科目
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="treeData"
        style="width: 100%;"
        row-key="unique_key"
        border
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        :header-cell-style="{background:'#f5f7fa', color:'#606266', fontWeight:'bold'}"
        class="subject-table"
      >
        <el-table-column prop="name" label="科目名称" min-width="300" header-align="center" align="left">
            <template #default="scope">
                <span v-if="scope.row.isRoot" style="font-weight:bold; color:#303133;">
                    <el-icon style="vertical-align: middle; margin-right:5px; color:#E6A23C"><FolderOpened /></el-icon>
                    {{ scope.row.name }}
                </span>
                <span v-else style="margin-left: 4px;">
                    <el-icon style="vertical-align: middle; margin-right:5px; color:#909399"><Document /></el-icon>
                    {{ scope.row.name }}
                </span>
            </template>
        </el-table-column>

        <el-table-column prop="code" label="科目编码" width="200" align="center">
            <template #default="scope">
                <el-tag v-if="scope.row.code" type="info" effect="plain" style="font-family: Consolas;">{{ scope.row.code }}</el-tag>
            </template>
        </el-table-column>

        <el-table-column prop="direction" label="余额方向" width="150" align="center">
             <template #default="scope">
                 <div v-if="!scope.row.isRoot">
                     <el-tag v-if="scope.row.direction === '借' || scope.row.balance_direction === 'DEBIT'" type="success" effect="light" round>借</el-tag>
                     <el-tag v-else type="warning" effect="light" round>贷</el-tag>
                 </div>
             </template>
        </el-table-column>

        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="scope">
            <div v-if="scope.row.isRoot">
                <el-button type="primary" link size="small" @click="openAddDialog(scope.row)">
                    <el-icon><Plus /></el-icon> 新增科目
                </el-button>
            </div>
            <div v-else>
                <el-button type="primary" link size="small" @click="openAddDialog(scope.row)">
                    + 子科目
                </el-button>
                <el-popconfirm title="确定删除该科目吗？" @confirm="handleDelete(scope.row)" width="200">
                    <template #reference>
                        <el-button type="danger" link size="small">
                            <el-icon><Delete /></el-icon> 删除
                        </el-button>
                    </template>
                </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="上级科目">
            <el-input :model-value="parentName" disabled placeholder="无 (作为一级科目)" />
        </el-form-item>
        <el-form-item label="科目类别">
             <el-select v-model="form.type" :disabled="isTypeDisabled" placeholder="请选择类别" style="width:100%">
                 <el-option label="资产" value="ASSET" />
                 <el-option label="负债" value="LIABILITY" />
                 <el-option label="权益" value="EQUITY" />
                 <el-option label="成本" value="COST" />
                 <el-option label="损益" value="PROFIT_LOSS" />
             </el-select>
        </el-form-item>
        <el-form-item label="科目编码">
            <el-input v-model="form.code" placeholder="例如: 100101" />
        </el-form-item>
        <el-form-item label="科目名称">
            <el-input v-model="form.name" placeholder="请输入科目名称" />
        </el-form-item>
        <el-form-item label="余额方向">
            <el-radio-group v-model="form.balance_direction">
                <el-radio label="DEBIT">借方</el-radio>
                <el-radio label="CREDIT">贷方</el-radio>
            </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Collection, MagicStick, FolderOpened, Document } from '@element-plus/icons-vue'

const treeData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isTypeDisabled = ref(false)

const form = ref({ code: '', name: '', type: '', balance_direction: 'DEBIT', parent_id: null })
const parentName = ref('')

// 定义五大类根节点，这里是虚拟节点
const rootTypes = [
    { unique_key: 'root_ASSET', name: '资产类', type: 'ASSET', isRoot: true, balance_direction: 'DEBIT', children: [] },
    { unique_key: 'root_LIABILITY', name: '负债类', type: 'LIABILITY', isRoot: true, balance_direction: 'CREDIT', children: [] },
    { unique_key: 'root_EQUITY', name: '权益类', type: 'EQUITY', isRoot: true, balance_direction: 'CREDIT', children: [] },
    { unique_key: 'root_COST', name: '成本类', type: 'COST', isRoot: true, balance_direction: 'DEBIT', children: [] },
    { unique_key: 'root_PROFIT_LOSS', name: '损益类', type: 'PROFIT_LOSS', isRoot: true, balance_direction: 'CREDIT', children: [] },
]

const loadList = async () => {
    try {
        const res = await axios.get('/api/subject')
        const list = res.data.data || []
        const roots = JSON.parse(JSON.stringify(rootTypes))
        const map = {}
        list.forEach(item => { item.unique_key = item.id; item.children = []; map[item.id] = item })
        list.forEach(item => {
            if (item.parent_id && map[item.parent_id]) {
                map[item.parent_id].children.push(item)
            } else {
                let typeKey = item.type_code || (item.type === '资产' ? 'ASSET' : item.type === '负债' ? 'LIABILITY' : item.type === '权益' ? 'EQUITY' : item.type === '成本' ? 'COST' : 'PROFIT_LOSS')
                const rootNode = roots.find(r => r.type === typeKey)
                if(rootNode) rootNode.children.push(item)
            }
        })
        treeData.value = roots
    } catch(e) { console.error(e) }
}

const openAddDialog = (row) => {
    form.value = { code: '', name: '', type: 'ASSET', balance_direction: 'DEBIT', parent_id: null }

    if (row) {
        isTypeDisabled.value = true
        if (row.isRoot) {
            parentName.value = row.name
            form.value.type = row.type
            form.value.balance_direction = row.balance_direction
            form.value.parent_id = null
        } else {
            parentName.value = `${row.code} ${row.name}`
            form.value.parent_id = row.id
            form.value.type = row.type_code || row.type
            form.value.code = row.code
            form.value.balance_direction = row.balance_direction === '借' ? 'DEBIT' : 'CREDIT'
        }
    } else {
        isTypeDisabled.value = false
        parentName.value = '无 (一级科目)'
        form.value.type = 'ASSET'
    }
    dialogTitle.value = '新增会计科目'
    dialogVisible.value = true
}

const handleSubmit = async () => {
    if(!form.value.code || !form.value.name) return ElMessage.warning('请填写完整信息')
    await axios.post('/api/subject', form.value)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadList()
}

const handleInit = async () => {
    ElMessageBox.confirm('确定要一键生成标准科目吗？', '提示').then(async () => {
        const res = await axios.post('/api/subject', { action: 'init' })
        ElMessage.success(res.data.message)
        loadList()
    })
}

const handleDelete = async (row) => {
    await axios.delete(`/api/subject?id=${row.id}`)
    ElMessage.success('删除成功')
    loadList()
}

onMounted(() => loadList())
</script>

<style scoped>
.app-container { width: 100%; }
.subject-card { width: 100%; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; }
.title-icon { font-size: 20px; color: #409EFF; margin-right: 8px; background: #ecf5ff; padding: 6px; border-radius: 6px; }
.title-text { font-size: 16px; font-weight: 600; color: #303133; }
.subject-table { margin-top: 10px; }
</style>