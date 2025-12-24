<template>
  <div class="app-container">
    <el-card shadow="never" class="print-card">
      <template #header>
        <div class="no-print" style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 18px;">资产负债表</span>
          <div style="display: flex; gap: 10px; align-items: center;">
            <span style="font-size: 14px; color: #666;">报表日期：</span>
            <el-date-picker
                v-model="queryDate" type="date" placeholder="选择日期"
                value-format="YYYY-MM-DD" :clearable="false" style="width: 150px;"
            />
            <el-button type="primary" :loading="loading" @click="loadData">生成报表</el-button>
            <el-button @click="printReport">打印</el-button>
          </div>
        </div>
      </template>

      <div v-if="reportData" class="report-paper">
        <h2 class="report-title">资 产 负 债 表</h2>
        <div class="report-info">
            <span>编制单位：{{ companyName }}</span>
            <span>日期：{{ queryDate }}</span>
            <span>单位：元</span>
        </div>

        <table class="standard-table">
            <thead>
                <tr class="header-row">
                    <th style="width: 20%">资 产</th>
                    <th style="width: 5%">行次</th>
                    <th style="width: 12%">期末余额</th>
                    <th style="width: 12%">年初余额</th>
                    <th style="width: 2%"></th> <th style="width: 20%">负债和所有者权益</th>
                    <th style="width: 5%">行次</th>
                    <th style="width: 12%">期末余额</th>
                    <th style="width: 12%">年初余额</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(row, index) in tableRows" :key="index">
                    <td class="text-left">{{ row.asset ? row.asset.name : '' }}</td>
                    <td class="text-center">{{ row.asset ? index + 1 : '' }}</td>
                    <td class="money">{{ row.asset ? formatMoney(row.asset.closing_balance) : '' }}</td>
                    <td class="money">{{ row.asset ? formatMoney(row.asset.opening_balance) : '' }}</td>

                    <td class="separator"></td>

                    <td class="text-left">{{ row.liability ? row.liability.name : '' }}</td>
                    <td class="text-center">{{ row.liability ? index + 1 : '' }}</td>
                    <td class="money">{{ row.liability ? formatMoney(row.liability.closing_balance) : '' }}</td>
                    <td class="money">{{ row.liability ? formatMoney(row.liability.opening_balance) : '' }}</td>
                </tr>

                <tr class="total-row">
                    <td class="text-left">资产总计</td>
                    <td></td>
                    <td class="money">{{ formatMoney(reportData.total_asset_end) }}</td>
                    <td class="money">{{ formatMoney(reportData.total_asset_begin) }}</td>
                    <td></td>
                    <td class="text-left">负债和所有者权益总计</td>
                    <td></td>
                    <td class="money">{{ formatMoney(reportData.total_le_end) }}</td>
                    <td class="money">{{ formatMoney(reportData.total_le_begin) }}</td>
                </tr>
            </tbody>
        </table>

        <div class="report-footer no-print">
            <span v-if="reportData.is_balanced" style="color: green;">
                <el-icon><CircleCheckFilled /></el-icon> 报表平衡
            </span>
            <span v-else style="color: red;">
                <el-icon><CircleCloseFilled /></el-icon> 报表不平 (差额: {{ (reportData.total_asset_end - reportData.total_le_end).toFixed(2) }})
            </span>
        </div>
      </div>

      <el-empty v-else description="请选择日期并点击生成报表" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'

const companyName = ref('未来科技贸易有限公司')
const queryDate = ref(new Date().toISOString().split('T')[0])
const reportData = ref(null)
const loading = ref(false)

// 组合左右两边的数据，生成统一的行
const tableRows = computed(() => {
    if (!reportData.value) return []
    const assets = reportData.value.assets
    const rights = reportData.value.liabilities_equity
    const maxLen = Math.max(assets.length, rights.length)

    const rows = []
    for (let i = 0; i < maxLen; i++) {
        rows.push({
            asset: assets[i] || null,
            liability: rights[i] || null
        })
    }
    return rows
})

const formatMoney = (val) => {
    if(val === 0 || val === '0') return '-'
    return Number(val).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}

const loadData = async () => {
    loading.value = true
    try {
        const res = await axios.post('/api/balance_sheet', { date: queryDate.value })
        if(res.data.code === 200) {
            reportData.value = res.data.data
            // 获取企业名称
            const info = await axios.get('/api/enterprise')
            if(info.data.data) companyName.value = info.data.data.name
            ElMessage.success('报表生成成功')
        } else {
            ElMessage.error(res.data.message)
        }
    } catch (error) {
        ElMessage.error('获取数据失败')
    } finally {
        loading.value = false
    }
}

const printReport = () => window.print()

onMounted(loadData)
</script>

<style scoped>
/* A4纸效果容器 */
.report-paper {
    width: 210mm; /* A4宽度 */
    min-height: 297mm;
    margin: 20px auto;
    background: #fff;
    padding: 20mm;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1); /* 阴影效果 */
    box-sizing: border-box;
}

.report-title {
    text-align: center;
    font-family: "SimSun", serif; /* 宋体 */
    font-size: 24px;
    margin-bottom: 20px;
    letter-spacing: 2px;
}

.report-info {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    margin-bottom: 10px;
    font-family: "SimSun", serif;
}

/* 标准财务表格样式 */
.standard-table {
    width: 100%;
    border-collapse: collapse;
    border: 2px solid #000; /* 外框加粗 */
    font-family: "SimSun", serif;
    font-size: 13px;
}

.standard-table th, .standard-table td {
    border: 1px solid #000; /* 细边框 */
    padding: 6px 4px;
    height: 28px;
}

.standard-table th {
    background-color: #f8f8f8;
    text-align: center;
    font-weight: bold;
}

.text-center { text-align: center; }
.text-left { text-align: left; padding-left: 5px; }
.money { text-align: right; font-family: "Arial", sans-serif; padding-right: 5px; }

.separator {
    background-color: #eee;
    border-top: none;
    border-bottom: none;
}

.total-row {
    background-color: #fff;
    font-weight: bold;
}

.report-footer {
    margin-top: 20px;
    text-align: center;
    font-size: 14px;
}

/* 打印时的调整 */
@media print {
    .no-print { display: none !important; }
    .app-container { padding: 0; margin: 0; background: #fff; }
    .el-card { border: none; box-shadow: none; margin: 0; }
    .report-paper {
        box-shadow: none;
        margin: 0;
        width: 100%;
        padding: 0;
    }
}
</style>