<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div class="header-left">
             <el-icon class="title-icon"><Sell /></el-icon>
             <span class="title-text">销售订单管理 (UC005)</span>
          </div>
          <el-button type="primary" color="#67C23A" @click="openCreateDialog" style="color: white">
            <el-icon style="margin-right: 5px"><Plus /></el-icon> 新建销售单
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" border stripe style="width: 100%" :header-cell-style="{background:'#f5f7fa', color:'#606266', fontWeight:'bold'}">
        <el-table-column type="expand">
          <template #default="props">
            <div style="padding: 10px 20px; background: #f0f9eb;">
                <el-table :data="props.row.items" size="small" border>
                <el-table-column prop="product_name" label="商品名称" />
                <el-table-column prop="subject_name" label="收入科目" width="150" />
                <el-table-column prop="quantity" label="数量" width="100" align="center" />
                <el-table-column prop="price" label="单价" width="120" align="right" />
                <el-table-column label="税率" width="100" align="center">
                    <template #default="scope">{{ (scope.row.tax_rate * 100).toFixed(0) }}%</template>
                </el-table-column>
                <el-table-column prop="amount" label="含税小计" width="120" align="right" />
                <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
              </el-table>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="order_no" label="订单编号" min-width="160" show-overflow-tooltip />
        <el-table-column prop="customer_name" label="客户" min-width="140" show-overflow-tooltip />
        <el-table-column prop="sales_date" label="销售日期" width="110" align="center" />
        <el-table-column prop="credit_period" label="账期" width="70" align="center" />
        <el-table-column prop="total_amount" label="总金额(含税)" width="130" align="right">
            <template #default="scope">
                <span style="color:#67C23A;font-weight:bold; font-family: Consolas;">¥ {{scope.row.total_amount}}</span>
            </template>
        </el-table-column>

        <el-table-column label="状态" width="220" align="center">
            <template #default="scope">
                <div style="display: flex; gap: 4px; justify-content: center;">
                    <el-tag type="success" effect="plain" size="small">已审核</el-tag>
                    <el-tag :type="scope.row.is_posted ? 'success' : 'info'" effect="light" size="small">
                        {{ scope.row.is_posted ? '已过账' : '未过账' }}
                    </el-tag>
                    <el-tag :type="scope.row.is_settled ? 'success' : 'info'" effect="light" size="small">
                        {{ scope.row.is_settled ? '已收款' : '未收款' }}
                    </el-tag>
                </div>
            </template>
        </el-table-column>

        <el-table-column label="操作" width="230" fixed="right" align="center">
          <template #default="scope">
            <el-tooltip content="修改订单" placement="top" v-if="!scope.row.is_posted && !scope.row.is_settled">
                <el-button type="primary" link :icon="Edit" @click="openEditDialog(scope.row)" />
            </el-tooltip>
            <el-tooltip content="删除订单" placement="top">
                <el-button type="danger" link :icon="Delete" @click="handleDelete(scope.row)" />
            </el-tooltip>
            <el-button v-if="!scope.row.is_posted" type="success" link size="small" @click="openPostDialog(scope.row)" style="margin-left: 8px;">
                <el-icon style="margin-right: 2px"><Tickets /></el-icon>生成凭证
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createDialogVisible" :title="isEditMode ? '修改销售订单' : '新建销售订单'" width="950px" align-center>
      <el-form :model="createForm" label-width="80px">
        <el-row :gutter="20">
            <el-col :span="8">
                <el-form-item label="客户">
                    <el-select v-model="createForm.customer_id" style="width:100%" placeholder="选择客户" @change="handleCustomerChange">
                        <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id"/>
                    </el-select>
                </el-form-item>
            </el-col>
            <el-col :span="8">
                <el-form-item label="日期"><el-date-picker v-model="createForm.sales_date" type="date" value-format="YYYY-MM-DD" style="width:100%"/></el-form-item>
            </el-col>
            <el-col :span="8">
                <el-form-item label="账期(天)"><el-input-number v-model="createForm.credit_period" :min="0" style="width:100%"/></el-form-item>
            </el-col>
        </el-row>

        <div style="margin:10px 0; border-top: 1px dashed #eee; padding-top: 10px;">
            <span style="font-weight: bold; font-size: 14px; margin-right: 10px;">商品明细</span>
            <el-button type="primary" link @click="addCreateItem">+ 添加商品</el-button>
        </div>

        <el-table :data="createForm.items" border size="small">
            <el-table-column label="商品名称" width="160">
                <template #default="scope"><el-input v-model="scope.row.product_name" placeholder="品名"/></template>
            </el-table-column>

            <el-table-column label="收入科目" width="160">
                <template #default="scope">
                    <el-select v-model="scope.row.subject_id" placeholder="请选择" filterable>
                         <el-option v-for="s in incomeSubjects" :key="s.id" :label="s.code+' '+s.name" :value="s.id" />
                    </el-select>
                </template>
            </el-table-column>

            <el-table-column label="数量" width="90">
                <template #default="scope"><el-input-number v-model="scope.row.quantity" :min="1" style="width:100%" :controls="false" /></template>
            </el-table-column>
            <el-table-column label="单价" width="110">
                <template #default="scope"><el-input-number v-model="scope.row.price" :precision="2" :min="0" style="width:100%" :controls="false" /></template>
            </el-table-column>

            <el-table-column label="税率(%)" width="110">
                <template #default="scope">
                     <el-input-number v-model="scope.row.tax_rate" :min="0" :max="100" :precision="0" :controls="false" style="width: 100%">
                         <template #suffix>%</template>
                     </el-input-number>
                </template>
            </el-table-column>

            <el-table-column label="含税小计" width="110" align="right">
                <template #default="scope">
                    ¥ {{ (scope.row.quantity * scope.row.price * (1 + scope.row.tax_rate/100)).toFixed(2) }}
                </template>
            </el-table-column>

            <el-table-column label="备注">
                <template #default="scope"><el-input v-model="scope.row.remark" placeholder="备注"/></template>
            </el-table-column>
            <el-table-column width="60" align="center" label="操作">
                <template #default="scope">
                    <el-button type="danger" link :icon="Delete" @click="removeCreateItem(scope.$index)"></el-button>
                </template>
            </el-table-column>
        </el-table>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible=false">取消</el-button>
        <el-button type="primary" color="#67C23A" @click="handleCreateSubmit" style="color: white">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="postDialogVisible" title="确认销售出库并生成凭证" width="800px" align-center>
        <el-alert title="系统将自动生成以下会计分录（已自动分离销项税额），请确认。" type="success" :closable="false" style="margin-bottom: 15px;" />
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
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete, Tickets, Sell, Plus } from '@element-plus/icons-vue'

const tableData = ref([])
const customerList = ref([])
const subjectList = ref([])

// 筛选收入类科目
const incomeSubjects = computed(() => {
    return subjectList.value.filter(s => ['PROFIT_LOSS'].includes(s.type_code))
})

const createDialogVisible = ref(false)
const isEditMode = ref(false)
const createForm = ref({ id: null, customer_id: '', sales_date: '', credit_period: 0, items: [] })

const postDialogVisible = ref(false)
const currentOrder = ref(null)
const voucherRows = ref([])

const loadOrders = async () => {
  const res = await axios.get('/api/sales_order')
  tableData.value = res.data.data
}
const loadCustomers = async () => {
  const res = await axios.get('/api/customer')
  customerList.value = res.data.data
}
const loadSubjects = async () => {
  const res = await axios.get('/api/subject')
  subjectList.value = res.data.data
}

// 客户改变联动账期
const handleCustomerChange = (val) => {
    const customer = customerList.value.find(c => c.id === val)
    if(customer) {
        createForm.value.credit_period = customer.default_credit_period || 0
    }
}

const openCreateDialog = async () => {
  await loadCustomers()
  await loadSubjects()
  isEditMode.value = false
  // 默认主营业务收入
  const defaultSub = subjectList.value.find(s => s.code === '6001')

  createForm.value = {
    id: null,
    customer_id: '',
    sales_date: new Date().toISOString().split('T')[0],
    credit_period: 0,
    items: [{product_name: '', quantity: 1, price: 0, tax_rate: 0, subject_id: defaultSub?.id, remark: ''}]
  }
  createDialogVisible.value = true
}

const openEditDialog = async (row) => {
  await loadCustomers()
  await loadSubjects()
  isEditMode.value = true
  const rowData = JSON.parse(JSON.stringify(row))

  if (rowData.items) {
      rowData.items.forEach(item => {
          item.tax_rate = item.tax_rate * 100
      })
  } else {
      const defaultSub = subjectList.value.find(s => s.code === '6001')
      rowData.items = [{product_name: '', quantity: 1, price: 0, tax_rate: 0, subject_id: defaultSub?.id, remark: ''}]
  }

  createForm.value = rowData
  createDialogVisible.value = true
}

const addCreateItem = () => {
    const defaultSub = subjectList.value.find(s => s.code === '6001')
    createForm.value.items.push({product_name: '', quantity: 1, price: 0, tax_rate: 0, subject_id: defaultSub?.id, remark: ''})
}
const removeCreateItem = (i) => createForm.value.items.splice(i, 1)

const handleCreateSubmit = async () => {
  if(!createForm.value.customer_id) return ElMessage.warning('请选择客户')

  const submitData = JSON.parse(JSON.stringify(createForm.value))

  for(let item of submitData.items){
      if(!item.subject_id) return ElMessage.warning('请选择收入科目')
      item.tax_rate = item.tax_rate / 100
  }

  const url = '/api/sales_order'
  const method = isEditMode.value ? axios.put : axios.post

  const res = await method(url, submitData)
  if (res.data.code === 200) {
      ElMessage.success('保存成功')
      createDialogVisible.value = false
      loadOrders()
  } else {
      ElMessage.error(res.data.message)
  }
}

// === 核心逻辑修改：价税分离 ===
const openPostDialog = async (row) => {
  currentOrder.value = row
  await loadSubjects()

  // 借：应收账款 (1122) - 总额
  // 贷：收入科目 (Net Amount)
  // 贷：应交税费 (Tax Amount) (2221)

  const sub1122 = subjectList.value.find(s => s.code === '1122') // 应收账款
  const sub2221 = subjectList.value.find(s => s.code === '2221') // 应交税费

  const rows = []

  // 1. 借方：应收账款 (总额)
  rows.push({
      summary: `销售-${row.customer_name}`,
      subject_id: sub1122?.id,
      debit: Number(row.total_amount),
      credit: 0
  })

  const creditMap = {}
  let totalTax = 0

  row.items.forEach(item => {
      const subId = item.subject_id
      const netAmount = item.price * item.quantity // 不含税
      const taxAmount = netAmount * item.tax_rate

      if(!creditMap[subId]) creditMap[subId] = 0
      creditMap[subId] += netAmount
      totalTax += taxAmount
  })

  // 2. 贷方：收入科目 (不含税)
  for(const [subId, amt] of Object.entries(creditMap)){
      const sub = subjectList.value.find(s => s.id == subId)
      if(amt > 0) {
          rows.push({
              summary: `销售收入-${sub?.name}`,
              subject_id: Number(subId),
              debit: 0,
              credit: Number(amt.toFixed(2))
          })
      }
  }

  // 3. 贷方：应交税费 (销项税)
  if (totalTax > 0.001) {
      rows.push({
          summary: `销售销项税额-${row.customer_name}`,
          subject_id: sub2221?.id,
          debit: 0,
          credit: Number(totalTax.toFixed(2))
      })
  }

  // 平账逻辑
  const totalCredit = rows.reduce((sum, r) => sum + r.credit, 0)
  const diff = Number(row.total_amount) - totalCredit
  if (Math.abs(diff) > 0 && Math.abs(diff) < 0.1) {
      // 补差额到最后一个贷方分录
      rows[rows.length-1].credit += diff
      rows[rows.length-1].credit = Number(rows[rows.length-1].credit.toFixed(2))
  }

  voucherRows.value = rows
  postDialogVisible.value = true
}

const handlePostSubmit = async () => {
  const res = await axios.post('/api/generate_voucher', {
    order_id: currentOrder.value.id,
    type: 'SALES',
    rows: voucherRows.value
  })
  if (res.data.code === 200) {
    ElMessage.success('凭证生成成功')
    postDialogVisible.value = false
    loadOrders()
  } else {
    ElMessage.error(res.data.message)
  }
}

const handleDelete = (row) => {
    ElMessageBox.confirm(
        `确定要删除销售单 ${row.order_no} 吗？`, '级联删除警告',
        { confirmButtonText: '确定删除', type: 'warning' }
    ).then(async () => {
        const res = await axios.delete(`/api/sales_order?id=${row.id}`)
        if (res.data.code === 200) { ElMessage.success('删除成功'); loadOrders(); }
        else { ElMessage.error(res.data.message); }
    })
}

onMounted(() => { loadOrders(); loadCustomers(); loadSubjects(); })
</script>

<style scoped>
.app-container { width: 100%; }
.header-left { display: flex; align-items: center; }
.title-icon { font-size: 20px; color: #409EFF; margin-right: 8px; background: #ecf5ff; padding: 6px; border-radius: 6px; }
.title-text { font-size: 16px; font-weight: 600; color: #303133; }
</style>