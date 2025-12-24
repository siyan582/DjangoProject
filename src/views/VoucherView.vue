<template>
  <div class="app-container">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="title-icon"><Collection /></el-icon>
            <span class="title-text">会计凭证一览表 (UC006)</span>
          </div>
          <el-button type="primary" @click="openManualDialog">
              <el-icon style="margin-right:5px"><EditPen /></el-icon> 手工录入凭证
          </el-button>
        </div>
      </template>

      <div class="filter-container">
        <el-form :inline="true" :model="queryParams" size="default" class="search-form">
          <el-form-item label="凭证日期">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="-"
              start-placeholder="开始"
              end-placeholder="结束"
              value-format="YYYY-MM-DD"
              style="width: 220px"
              :shortcuts="shortcuts"
            />
          </el-form-item>

          <el-form-item label="科目">
            <el-input v-model="queryParams.subject" placeholder="科目名称或代码" clearable style="width: 140px" />
          </el-form-item>

          <el-form-item label="整单备注">
            <el-input v-model="queryParams.remark" placeholder="如：月末计提" clearable style="width: 140px" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch" plain>
              <el-icon><Search /></el-icon> 查询
            </el-button>
            <el-button @click="resetSearch" plain>重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="tableData" border style="width: 100%" stripe size="small" :header-cell-style="{background:'#f5f7fa', color:'#606266', fontWeight:'normal'}">
        <el-table-column prop="date" label="日期" width="100" align="center" sortable />

        <el-table-column prop="voucher_no" label="凭证字号" width="140" align="center">
            <template #default="scope">
                <span class="voucher-no-tag">{{ scope.row.voucher_no }}</span>
            </template>
        </el-table-column>

        <el-table-column label="会计分录" min-width="360">
          <template #default="scope">
            <div class="entries-wrapper">
              <div v-for="(item, index) in scope.row.details" :key="index" class="entry-row">

                <div class="entry-info">
                  <span class="subject-name">{{ item.subject_name }}</span>
                  <span class="summary-text" v-if="item.summary">({{ item.summary }})</span>
                </div>

                <div class="entry-amount">
                  <div v-if="Number(item.debit) > 0" class="amount-wrap debit">
                     <span class="direction-tag debit">借</span>
                     <span class="money-text">¥ {{ Number(item.debit).toFixed(2) }}</span>
                  </div>
                  <div v-if="Number(item.credit) > 0" class="amount-wrap credit">
                     <span class="direction-tag credit">贷</span>
                     <span class="money-text">¥ {{ Number(item.credit).toFixed(2) }}</span>
                  </div>
                 </div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="remark" label="整单备注" min-width="200" show-overflow-tooltip />

        <el-table-column label="操作" width="80" align="center" fixed="right">
          <template #default="scope">
              <el-button type="danger" link size="small" :icon="Delete" @click="handleDelete(scope.row)"></el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="manualVisible" title="手工录入会计凭证" width="900px" align-center>
        <el-form label-width="80px">
            <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="凭证日期">
                        <el-date-picker v-model="manualForm.date" type="date" value-format="YYYY-MM-DD" style="width: 100%"/>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="整单备注">
                        <el-input v-model="manualForm.remark" placeholder="例如：月末计提工资"/>
                    </el-form-item>
                </el-col>
            </el-row>

            <div style="margin-bottom: 10px; display:flex; justify-content:space-between; align-items:center; background:#f5f7fa; padding:8px; border-radius:4px;">
                 <span style="font-size:13px; color:#606266;">分录明细</span>
                 <el-button type="primary" link size="small" @click="addManualRow">+ 添加一行</el-button>
            </div>

            <el-table :data="manualRows" border size="small">
                <el-table-column label="摘要">
                    <template #default="scope"><el-input v-model="scope.row.summary" placeholder="摘要" /></template>
                </el-table-column>
                <el-table-column label="科目" width="220">
                    <template #default="scope">
                        <el-select v-model="scope.row.subject_id" filterable placeholder="选择科目" style="width: 100%">
                            <el-option v-for="s in subjectList" :key="s.id" :label="s.code+' '+s.name" :value="s.id"/>
                        </el-select>
                    </template>
                </el-table-column>
                <el-table-column label="借方金额" width="150">
                    <template #default="scope"><el-input-number v-model="scope.row.debit" :controls="false" :min="0" :precision="2" style="width: 100%"/></template>
                </el-table-column>
                <el-table-column label="贷方金额" width="150">
                    <template #default="scope"><el-input-number v-model="scope.row.credit" :controls="false" :min="0" :precision="2" style="width: 100%"/></template>
                </el-table-column>
                <el-table-column width="60" align="center">
                    <template #default="scope">
                        <el-button type="danger" link :icon="Delete" @click="removeManualRow(scope.$index)"></el-button>
                    </template>
                </el-table-column>
            </el-table>

            <div style="margin-top: 15px; text-align: right; font-size: 14px;">
                <span style="margin-right: 20px;">借方合计: <b>{{ totalDebit.toFixed(2) }}</b></span>
                <span>贷方合计: <b>{{ totalCredit.toFixed(2) }}</b></span>
                <span v-if="totalDebit !== totalCredit" style="color: #F56C6C; margin-left: 10px; font-weight:bold;">(不平衡)</span>
                <span v-else style="color: #67C23A; margin-left: 10px; font-weight:bold;">(平衡)</span>
            </div>
        </el-form>
        <template #footer>
            <el-button @click="manualVisible = false">取消</el-button>
            <el-button type="success" @click="handleManualSubmit">保存凭证</el-button>
        </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, EditPen, Search, Collection, Delete } from '@element-plus/icons-vue'

const tableData = ref([])
const subjectList = ref([])
const manualVisible = ref(false)
const manualForm = ref({ date: '', remark: '' })
const manualRows = ref([])

// === 搜索相关变量 ===
const dateRange = ref([])
// 移除了 summary 参数
const queryParams = ref({ subject: '', remark: '' })

const shortcuts = [
  { text: '最近一周', value: () => { const end = new Date(); const start = new Date(); start.setTime(start.getTime() - 3600 * 1000 * 24 * 7); return [start, end] } },
  { text: '最近一个月', value: () => { const end = new Date(); const start = new Date(); start.setTime(start.getTime() - 3600 * 1000 * 24 * 30); return [start, end] } },
]

const loadVouchers = async () => {
  let url = '/api/voucher?'
  if(dateRange.value && dateRange.value.length === 2) {
      url += `start_date=${dateRange.value[0]}&end_date=${dateRange.value[1]}&`
  }
  if(queryParams.value.subject) {
      url += `subject=${queryParams.value.subject}&`
  }
  if(queryParams.value.remark) {
      url += `remark=${queryParams.value.remark}&`
  }
  // 移除了 summary 的 url 拼接

  const res = await axios.get(url)
  tableData.value = res.data.data
}

const handleSearch = () => loadVouchers()

const resetSearch = () => {
    dateRange.value = []
    queryParams.value = { subject: '', remark: '' }
    loadVouchers()
}

const openManualDialog = async () => {
    const res = await axios.get('/api/subject')
    subjectList.value = res.data.data
    manualForm.value = { date: new Date().toISOString().split('T')[0], remark: '' }
    manualRows.value = [
        { summary: '', subject_id: '', debit: 0, credit: 0 },
        { summary: '', subject_id: '', debit: 0, credit: 0 }
    ]
    manualVisible.value = true
}

const addManualRow = () => manualRows.value.push({ summary: '', subject_id: '', debit: 0, credit: 0 })
const removeManualRow = (idx) => manualRows.value.splice(idx, 1)

const totalDebit = computed(() => manualRows.value.reduce((sum, r) => sum + Number(r.debit), 0))
const totalCredit = computed(() => manualRows.value.reduce((sum, r) => sum + Number(r.credit), 0))

const handleManualSubmit = async () => {
    if (Math.abs(totalDebit.value - totalCredit.value) > 0.01) return ElMessage.error('借贷金额不平衡')
    if (totalDebit.value === 0) return ElMessage.warning('金额不能为0')

    const res = await axios.post('/api/generate_voucher', {
        type: 'MANUAL',
        rows: manualRows.value,
        remark: manualForm.value.remark,
        date: manualForm.value.date
    })

    if(res.data.code === 200) {
        ElMessage.success('凭证保存成功')
        manualVisible.value = false
        loadVouchers()
    } else {
        ElMessage.error(res.data.message)
    }
}

const handleDelete = (row) => {
    ElMessageBox.confirm('确定删除该凭证吗？', '警告', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }).then(async () => {
        const res = await axios.delete(`/api/voucher?id=${row.id}`)
        if(res.data.code === 200) { ElMessage.success('已删除'); loadVouchers() }
        else { ElMessage.error(res.data.message) }
    })
}

onMounted(() => loadVouchers())
</script>

<style scoped>
.app-container { width: 100%; }
.main-card { width: 100%; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; }
.title-icon { font-size: 20px; color: #409EFF; margin-right: 8px; background: #ecf5ff; padding: 6px; border-radius: 6px; }
.title-text { font-size: 16px; font-weight: 600; color: #303133; }

/* 修改点2：增加底部间距
  margin-bottom: 10px -> 25px
*/
.filter-container { margin-bottom: 25px; }

.search-form .el-form-item { margin-bottom: 0; margin-right: 12px; }

.voucher-no-tag {
    font-family: 'Consolas', monospace;
    font-weight: normal;
    color: #303133;
    background-color: #f4f4f5;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #e9e9eb;
}

.entries-wrapper {
    display: flex;
    flex-direction: column;
}
.entry-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px dashed #e4e7ed;
}
.entry-row:last-child {
    border-bottom: none;
}

.entry-info {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
}

.subject-name {
    font-weight: normal;
    color: #303133;
    font-size: 14px;
    margin-right: 6px;
}

.summary-text {
    font-size: 13px;
    color: #909399;
}

.entry-amount {
    text-align: right;
    white-space: nowrap;
}
.amount-wrap {
    display: flex;
    align-items: center;
    justify-content: flex-end;
}
.direction-tag {
    font-size: 12px;
    padding: 0 4px;
    border-radius: 3px;
    margin-right: 6px;
    transform: scale(0.9);
}
.direction-tag.debit {
    border: 1px solid #67C23A;
    color: #67C23A;
    background: #f0f9eb;
}
.direction-tag.credit {
    border: 1px solid #409EFF;
    color: #409EFF;
    background: #ecf5ff;
}

.money-text {
    font-family: 'Consolas', monospace;
    font-weight: normal;
    font-size: 14px;
}
.debit .money-text { color: #67C23A; }
.credit .money-text { color: #409EFF; }
</style>