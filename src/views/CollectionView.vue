<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">收款管理 (UC008)</span>
          <el-button type="success" @click="openCreateDialog">+ 新建收款单</el-button>
        </div>
      </template>

      <el-table :data="tableData" border stripe style="width: 100%">
        <el-table-column prop="collection_no" label="收款单号" width="180" show-overflow-tooltip />

        <el-table-column prop="date" label="日期" width="110" align="center" sortable />

        <el-table-column prop="customer_name" label="客户" min-width="120" show-overflow-tooltip />

        <el-table-column prop="order_no" label="关联销售单" min-width="160" show-overflow-tooltip>
            <template #default="scope">
                <el-tag v-if="scope.row.order_no !== '-'" type="info" size="small">{{ scope.row.order_no }}</el-tag>
                <span v-else>-</span>
            </template>
        </el-table-column>

        <el-table-column prop="amount" label="金额" width="130" align="right">
            <template #default="scope">
                <span style="color:#67C23A;font-weight:bold; font-family: Consolas;">+ ¥ {{scope.row.amount}}</span>
            </template>
        </el-table-column>

        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />

        <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="scope">
                <el-tag :type="scope.row.status==='已过账'?'success':'info'" size="small">{{ scope.row.status }}</el-tag>
            </template>
        </el-table-column>

        <el-table-column label="操作" width="140" fixed="right" align="center">
          <template #default="scope">
            <el-tooltip content="确认收款并过账" placement="top" v-if="scope.row.status === '未过账' || scope.row.status === 'CREATED'">
                <el-button type="success" link size="small" @click="openPostDialog(scope.row)">
                    过账
                </el-button>
            </el-tooltip>

            <el-tooltip content="删除记录" placement="top">
                <el-button type="danger" link :icon="Delete" @click="handleDelete(scope.row)" />
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createDialogVisible" title="新建收款单" width="600px">
        <el-form :model="createForm" label-width="100px">
            <el-form-item label="收款日期">
                <el-date-picker v-model="createForm.date" type="date" value-format="YYYY-MM-DD" style="width: 100%"/>
            </el-form-item>
            <el-form-item label="客户">
                <el-select v-model="createForm.customer_id" filterable placeholder="选择客户" style="width: 100%" @change="handleCustomerChange">
                    <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id"/>
                </el-select>
            </el-form-item>
            <el-form-item label="关联销售单">
                <el-select
                    v-model="createForm.order_id"
                    placeholder="先选客户，再选订单"
                    style="width: 100%"
                    clearable
                    @change="handleOrderChange"
                >
                    <el-option v-for="o in customerOrders" :key="o.id" :label="o.order_no + ' (¥' + o.total_amount + ')'" :value="o.id"/>
                </el-select>
            </el-form-item>
            <el-form-item label="收款金额">
                <el-input-number v-model="createForm.amount" :precision="2" style="width: 100%" />
            </el-form-item>
            <el-form-item label="备注">
                <el-input v-model="createForm.remark" type="textarea"/>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="createDialogVisible = false">取消</el-button>
            <el-button type="success" @click="handleCreateSubmit">保存</el-button>
        </template>
    </el-dialog>

    <el-dialog v-model="postDialogVisible" title="确认收款并生成凭证" width="800px">
        <el-table :data="voucherRows" border>
            <el-table-column prop="summary" label="摘要"></el-table-column>
            <el-table-column label="科目">
                <template #default="scope">
                    <el-select v-model="scope.row.subject_id" filterable style="width: 100%">
                        <el-option v-for="s in subjectList" :key="s.id" :label="s.code+' '+s.name" :value="s.id"/>
                    </el-select>
                </template>
            </el-table-column>
            <el-table-column label="借方" width="120"><template #default="scope">{{scope.row.debit}}</template></el-table-column>
            <el-table-column label="贷方" width="120"><template #default="scope">{{scope.row.credit}}</template></el-table-column>
        </el-table>
        <template #footer>
            <el-button @click="postDialogVisible = false">取消</el-button>
            <el-button type="success" @click="handlePostSubmit">确认生成</el-button>
        </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Delete } from '@element-plus/icons-vue'

const tableData = ref([])
const customerList = ref([])
const allOrders = ref([])
const customerOrders = ref([])
const subjectList = ref([])

const createDialogVisible = ref(false)
const createForm = ref({ date: '', customer_id: '', order_id: null, amount: 0, remark: '' })

const postDialogVisible = ref(false)
const currentRecord = ref(null)
const voucherRows = ref([])

const loadData = async () => {
    const res = await axios.get('/api/collection')
    // 后端返回 status 是 'CREATED' 或 'POSTED'，前端转换一下显示
    tableData.value = res.data.data.map(item => ({
        ...item,
        status: item.status === 'POSTED' ? '已过账' : '未过账'
    }))
    return res.data.data
}

const openCreateDialog = async () => {
    // 1. 获取客户列表
    const resCus = await axios.get('/api/customer')
    customerList.value = resCus.data.data

    // 2. 获取现有收款单，防止重复
    // 注意：从 API 重新拉取原始数据，比 tableData 里的更靠谱
    const resCol = await axios.get('/api/collection')
    const processingOrderNos = resCol.data.data.map(c => c.order_no)

    // 3. 获取所有销售订单
    const resOrd = await axios.get('/api/sales_order')

    // 4. 过滤：
    //  - is_posted (已生成销售凭证，确认是有效销售)
    //  - !is_settled (还未完全收款)
    //  - !processing (未在收款流程中)
    allOrders.value = resOrd.data.data.filter(o =>
        o.is_posted &&
        !o.is_settled &&
        !processingOrderNos.includes(o.order_no)
    )

    createForm.value = { date: new Date().toISOString().split('T')[0], customer_id: '', order_id: null, amount: 0, remark: '' }
    customerOrders.value = []
    createDialogVisible.value = true
}

const handleCustomerChange = (val) => {
    // 筛选出该客户的未结清订单
    customerOrders.value = allOrders.value.filter(o => o.customer_id === val)
    createForm.value.order_id = null
    createForm.value.amount = 0
}

// [核心修复] 自动填金额
const handleOrderChange = (val) => {
    const order = customerOrders.value.find(o => o.id === val)
    if (order) {
        createForm.value.amount = order.total_amount
    } else {
        createForm.value.amount = 0
    }
}

const handleCreateSubmit = async () => {
    const res = await axios.post('/api/collection', createForm.value)
    if(res.data.code === 200) {
        ElMessage.success('保存成功')
        createDialogVisible.value = false
        loadData()
    } else {
        ElMessage.error(res.data.message)
    }
}

const openPostDialog = async (row) => {
    currentRecord.value = row
    const res = await axios.get('/api/subject')
    subjectList.value = res.data.data

    // 借：银行存款(1002) 贷：应收账款(1122)
    const sub1002 = subjectList.value.find(s => s.code === '1002')
    const sub1122 = subjectList.value.find(s => s.code === '1122')

    voucherRows.value = [
        { summary: `收到货款-${row.customer_name}`, subject_id: sub1002?.id, debit: row.amount, credit: 0 },
        { summary: `核销应收-${row.customer_name}`, subject_id: sub1122?.id, debit: 0, credit: row.amount }
    ]
    postDialogVisible.value = true
}

const handlePostSubmit = async () => {
    const res = await axios.post('/api/generate_voucher', {
        order_id: currentRecord.value.id,
        type: 'COLLECTION',
        rows: voucherRows.value
    })
    if(res.data.code === 200) {
        ElMessage.success('过账成功')
        postDialogVisible.value = false
        loadData()
    } else {
        ElMessage.error(res.data.message)
    }
}

const handleDelete = (row) => {
    ElMessageBox.confirm('确定删除这条收款记录吗？\n如果已生成凭证，凭证也会被删除，且关联订单会回滚为未收款状态。', '级联删除警告', { type: 'warning' }).then(async () => {
        const res = await axios.delete(`/api/collection?id=${row.id}`)
        if(res.data.code === 200) {
            ElMessage.success('删除成功')
            loadData()
        } else {
            ElMessage.error(res.data.message)
        }
    })
}

onMounted(loadData)
</script>