<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="no-print" style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 18px;">现金流量表</span>
          <div style="display: flex; gap: 10px;">
            <el-date-picker
                v-model="dateRange" type="daterange" range-separator="至"
                start-placeholder="开始日期" end-placeholder="结束日期"
                value-format="YYYY-MM-DD" :clearable="false"
            />
            <el-button type="primary" @click="loadData">生成报表</el-button>
            <el-button @click="printReport">打印</el-button>
          </div>
        </div>
      </template>

      <div v-if="reportData" class="report-paper">
          <h2 class="report-title">现 金 流 量 表</h2>
          <div class="report-info">
            <span>编制单位：{{ companyName }}</span>
            <span>期间：{{dateRange[0]}} 至 {{dateRange[1]}}</span>
            <span>单位：元</span>
          </div>

          <table class="standard-table">
              <thead>
                  <tr>
                      <th style="width: 60%">项 目</th>
                      <th style="width: 10%">行次</th>
                      <th style="width: 30%">金额</th>
                  </tr>
              </thead>
              <tbody>
                  <tr class="section-header"><td>一、经营活动产生的现金流量</td><td></td><td></td></tr>

                  <tr><td class="indent">现金流入小计</td><td class="center">1</td><td class="money">{{ formatMoney(reportData.inflow) }}</td></tr>
                  <tr><td class="indent">现金流出小计</td><td class="center">2</td><td class="money">{{ formatMoney(reportData.outflow) }}</td></tr>

                  <tr class="total-row">
                      <td>经营活动产生的现金流量净额</td><td class="center">3</td>
                      <td class="money">{{ formatMoney(reportData.net_change) }}</td>
                  </tr>

                  <tr class="section-header"><td>二、期初现金余额</td><td></td><td></td></tr>
                  <tr><td class="indent">加：期初现金及现金等价物余额</td><td class="center">4</td><td class="money">{{ formatMoney(reportData.opening_balance) }}</td></tr>

                  <tr class="total-row">
                      <td>三、期末现金及现金等价物余额</td><td class="center">5</td>
                      <td class="money">{{ formatMoney(reportData.closing_balance) }}</td>
                  </tr>
              </tbody>
          </table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const companyName = ref('未来科技贸易有限公司')
const start = new Date(); start.setDate(1);
const today = new Date();
const dateRange = ref([start.toISOString().split('T')[0], today.toISOString().split('T')[0]])
const reportData = ref(null)

const formatMoney = (val) => {
    if(!val) return '-'
    return Number(val).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}

const loadData = async () => {
    const res = await axios.post('/api/cash_flow', {
        start_date: dateRange.value[0], end_date: dateRange.value[1]
    })
    try {
        const info = await axios.get('/api/enterprise')
        if(info.data.data) companyName.value = info.data.data.name
    } catch(e){}
    reportData.value = res.data.data
}

const printReport = () => window.print()
onMounted(loadData)
</script>

<style scoped>
/* 统一样式 */
.report-paper {
    width: 210mm; margin: 20px auto; background: #fff; padding: 20mm;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.report-title { text-align: center; font-family: "SimSun"; font-size: 24px; margin-bottom: 20px; }
.report-info { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 10px; font-family: "SimSun"; }
.standard-table { width: 100%; border-collapse: collapse; border: 2px solid #000; font-family: "SimSun"; font-size: 14px; }
.standard-table th, .standard-table td { border: 1px solid #000; padding: 8px; }
.standard-table th { background: #f8f8f8; text-align: center; }
.money { text-align: right; font-family: Arial; }
.center { text-align: center; }
.indent { padding-left: 2em; }
.section-header { font-weight: bold; background-color: #f9f9f9; }
.total-row { font-weight: bold; }

@media print {
    .no-print { display: none; }
    .report-paper { box-shadow: none; margin: 0; width: 100%; }
    .app-container { padding: 0; background: #fff; }
    .el-card { border: none; }
}
</style>