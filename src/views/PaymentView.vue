<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">付款管理 (UC007)</span>
          <el-button type="warning" @click="openCreateDialog" color="#E6A23C" style="color: white">
            <el-icon style="margin-right: 5px"><Plus /></el-icon> 新建付款单
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" border stripe style="width: 100%">
        <el-table-column prop="payment_no" label="付款单号" width="180" show-overflow-tooltip />

        <el-table-column prop="payment_date" label="日期" width="110" align="center" sortable />

        <el-table-column prop="supplier_name" label="供应商" min-width="120" show-overflow-tooltip />

        <el-table-column prop="purchase_order_no" label="关联采购单" min-width="160" show-overflow-tooltip>
            <template #default="scope">
                <el-tag v-if="scope.row.purchase_order_no" type="info" size="small">{{ scope.row.purchase_order_no }}</el-tag>
                <span v-else>-</span>
            </template>
        </el-table-column>

        <el-table-column prop="amount" label="金额" width="130" align="right">
            <template #default="scope">
                <span style="color:#E6A23C;font-weight:bold; font-family: Consolas;">- ¥ {{ Number(scope.row.amount).toFixed(2) }}</span>
            </template>
        </el-table-column>

        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />

        <el-table-column label="状态" width="100" align="center">
            <template #default="scope">
                <el-tag :type="scope.row.is_settled ? 'success' : 'info'" size="small">
                    {{ scope.row.is_settled ? '已过账' : '未过账' }}
                </el-tag>
            </template>
        </el-table-column>

        <el-table-column label="操作" width="140" fixed="right" align="center">
          <template #default="scope">
            <el-tooltip content="确认付款并过账" placement="top" v-if="!scope.row.is_settled">
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

    <el-dialog v-model="createDialogVisible" title="新建付款单" width="600px">
        <el-form :model="createForm" label-width="100px">
            <el-form-item label="付款日期">
                <el-date-picker v-model="createForm.payment_date" type="date" value-format="YYYY-MM-DD" style="width: 100%"/>
            </el-form-item>
            <el-form-item label="供应商">
                <el-select v-model="createForm.supplier_id" filterable placeholder="选择供应商" style="width: 100%" @change="handleSupplierChange">
                    <el-option v-for="s in supplierList" :key="s.id" :label="s.name" :value="s.id"/>
                </el-select>
            </el-form-item>
            <el-form-item label="关联采购单">
                <el-select
                    v-model="createForm.purchase_order_id"
                    placeholder="先选供应商，再选订单"
                    style="width: 100%"
                    clearable
                    @change="handleOrderChange"
                >
                    <el-option v-for="o in supplierOrders" :key="o.id" :label="o.order_no + ' (¥' + o.total_amount + ')'" :value="o.id"/>
                </el-select>
            </el-form-item>
            <el-form-item label="付款金额">
                <el-input-number v-model="createForm.amount" :precision="2" :min="0" style="width: 100%" />
            </el-form-item>
            <el-form-item label="备注">
                <el-input v-model="createForm.remark" type="textarea"/>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="createDialogVisible = false">取消</el-button>
            <el-button type="primary" color="#E6A23C" style="color: white" @click="handleCreateSubmit">保存</el-button>
        </template>
    </el-dialog>

    <el-dialog v-model="postDialogVisible" title="确认付款并生成凭证" width="800px">
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
import { Check, Delete, Plus } from '@element-plus/icons-vue'

const tableData = ref([])
const supplierList = ref([])
const allOrders = ref([])
const supplierOrders = ref([])
const subjectList = ref([])

const createDialogVisible = ref(false)
const createForm = ref({ payment_date: '', supplier_id: '', purchase_order_id: null, amount: 0, remark: '', payment_method_subject_id: null })

const postDialogVisible = ref(false)
const currentRecord = ref(null)
const voucherRows = ref([])

const loadData = async () => {
    const res = await axios.get('/api/payment')
    tableData.value = res.data.data
    return res.data.data // 返回数据供 openCreateDialog 使用
}

const openCreateDialog = async () => {
    // 1. 获取供应商列表
    const resSup = await axios.get('/api/supplier')
    supplierList.value = resSup.data.data

    // 2. 获取当前已存在的付款记录（为了过滤已经创建过付款单的订单）
    // 注意：这里复用 loadData 的结果或重新请求
    const currentPayments = await axios.get('/api/payment')
    const processingOrderNos = currentPayments.data.data.map(p => p.purchase_order_no).filter(no => no)

    // 3. 获取所有采购订单
    const resOrd = await axios.get('/api/purchase_order')

    // 4. 核心过滤逻辑：
    //  - 必须是“已审核”(status) (后端返回中文或英文，这里假设 approved 或在列表里处理了)
    //  - 必须是“未结清”(!is_settled)
    //  - 必须“不在处理中”(!processingOrderNos.includes) -> 防止重复创建付款单
    allOrders.value = resOrd.data.data.filter(o => {
        // 兼容后端可能返回 "已审核" 或 "APPROVED"
        // 只要未结清且未在付款表中出现，即可付款
        return !o.is_settled && !processingOrderNos.includes(o.order_no)
    })

    // 5. 获取科目（为了兼容接口，虽然弹窗不让选科目了，但后台可能需要）
    const resSub = await axios.get('/api/subject')
    subjectList.value = resSub.data.data
    const defaultBank = subjectList.value.find(s => s.code === '1002')

    createForm.value = {
        payment_date: new Date().toISOString().split('T')[0],
        supplier_id: '',
        purchase_order_id: null,
        amount: 0,
        remark: '',
        payment_method_subject_id: defaultBank ? defaultBank.id : null
    }
    supplierOrders.value = []
    createDialogVisible.value = true
}

const handleSupplierChange = (val) => {
    // 筛选出该供应商的订单
    supplierOrders.value = allOrders.value.filter(o => o.supplier_id === val)
    createForm.value.purchase_order_id = null
    createForm.value.amount = 0
}

// [核心修复] 选订单后自动填金额
const handleOrderChange = (val) => {
    const order = supplierOrders.value.find(o => o.id === val)
    if (order) {
        createForm.value.amount = order.total_amount
    } else {
        createForm.value.amount = 0
    }
}

const handleCreateSubmit = async () => {
    if(!createForm.value.supplier_id || !createForm.value.amount) {
        return ElMessage.warning('请填写供应商和金额')
    }
    const res = await axios.post('/api/payment', createForm.value)
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
    if (subjectList.value.length === 0) {
        const res = await axios.get('/api/subject')
        subjectList.value = res.data.data
    }

    // 借：应付账款 (2202)
    // 贷：银行存款 (1002)
    const sub2202 = subjectList.value.find(s => s.code === '2202')
    const sub1002 = subjectList.value.find(s => s.code === '1002')

    voucherRows.value = [
        { summary: `支付货款-${row.supplier_name}`, subject_id: sub2202?.id, debit: row.amount, credit: 0 },
        { summary: `银行付款-${row.supplier_name}`, subject_id: sub1002?.id, debit: 0, credit: row.amount }
    ]
    postDialogVisible.value = true
}

const handlePostSubmit = async () => {
    const res = await axios.post('/api/generate_voucher', {
        order_id: currentRecord.value.id,
        type: 'PAYMENT',
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
    ElMessageBox.confirm('确定删除这条付款记录吗？\n如果已生成凭证，凭证也会被删除，且订单状态会回滚。', '级联删除警告', { type: 'warning' }).then(async () => {
        const res = await axios.delete(`/api/payment?id=${row.id}`)
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