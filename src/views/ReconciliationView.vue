<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">期末对账 / 试算平衡表 (UC009)</span>
          <el-button type="primary" @click="loadData">
            <el-icon><Refresh /></el-icon> 刷新数据
          </el-button>
        </div>
      </template>

      <div style="margin-bottom: 20px;">
        <el-alert
          v-if="summary.is_balanced"
          title="账务平衡！借方发生额 = 贷方发生额，财务状况健康。"
          type="success"
          show-icon
          :closable="false"
        />
        <el-alert
          v-else
          title="账务不平衡！借贷不相等，请检查凭证录入是否有误。"
          type="error"
          show-icon
          :closable="false"
        />
      </div>

      <el-table :data="tableData" border stripe style="width: 100%">
        <el-table-column prop="code" label="科目编码" width="120" sortable />
        <el-table-column prop="name" label="科目名称" min-width="150" />
        <el-table-column prop="direction" label="余额方向" width="100" align="center">
             <template #default="scope">
                 <el-tag v-if="scope.row.direction === '借'" type="success">借</el-tag>
                 <el-tag v-else type="warning">贷</el-tag>
             </template>
        </el-table-column>

        <el-table-column label="本期借方发生额" align="right" min-width="150">
            <template #default="scope">
                {{ formatMoney(scope.row.period_debit) }}
            </template>
        </el-table-column>

        <el-table-column label="本期贷方发生额" align="right" min-width="150">
            <template #default="scope">
                {{ formatMoney(scope.row.period_credit) }}
            </template>
        </el-table-column>

        <el-table-column label="期末余额" align="right" min-width="150">
            <template #default="scope">
                <span :style="{ fontWeight: 'bold', color: scope.row.end_balance < 0 ? 'red' : '#303133' }">
                    {{ formatMoney(scope.row.end_balance) }}
                </span>
            </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border: 1px solid #ebeef5; text-align: right;">
          <span style="margin-right: 30px; font-size: 16px;">
              借方合计: <b style="color: #67C23A;">{{ formatMoney(summary.total_debit) }}</b>
          </span>
          <span style="font-size: 16px;">
              贷方合计: <b style="color: #409EFF;">{{ formatMoney(summary.total_credit) }}</b>
          </span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Refresh } from '@element-plus/icons-vue'

const tableData = ref([])
const summary = ref({ total_debit: 0, total_credit: 0, is_balanced: true })

const loadData = async () => {
  const res = await axios.get('/api/trial_balance')
  if (res.data.code === 200) {
      tableData.value = res.data.data.rows
      summary.value = {
          total_debit: res.data.data.total_debit,
          total_credit: res.data.data.total_credit,
          is_balanced: res.data.data.is_balanced
      }
  }
}

// 金额格式化函数 (加千分位)
const formatMoney = (val) => {
    if (!val) return '¥ 0.00'
    return '¥ ' + Number(val).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}

onMounted(() => {
  loadData()
})
</script>