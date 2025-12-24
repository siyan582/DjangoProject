<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="no-print" style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 18px;">利润表</span>
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
          <h2 class="report-title">利 润 表</h2>
          <div class="report-info">
            <span>编制单位：{{ companyName }}</span>
            <span>期间：{{dateRange[0]}} 至 {{dateRange[1]}}</span>
            <span>单位：元</span>
          </div>

          <table class="standard-table">
              <thead>
                  <tr>
                      <th style="width: 50%">项 目</th>
                      <th style="width: 10%">行次</th>
                      <th style="width: 40%">本期金额</th>
                  </tr>
              </thead>
              <tbody>
                  <tr class="section-header"><td>一、营业收入</td><td class="center">1</td><td class="money">{{ formatMoney(reportData.total_income) }}</td></tr>
                  <tr v-for="(item, idx) in incomes" :key="item.code">
                      <td class="indent">其中：{{ item.name }}</td>
                      <td class="center">{{ idx + 2 }}</td>
                      <td class="money">{{ formatMoney(item.amount) }}</td>
                  </tr>

                  <tr class="section-header"><td>二、营业成本</td><td class="center">10</td><td class="money">{{ formatMoney(costsTotal) }}</td></tr>
                  <tr v-for="(item, idx) in costs" :key="item.code">
                      <td class="indent">减：{{ item.name }}</td>
                      <td class="center">{{ idx + 11 }}</td>
                      <td class="money">{{ formatMoney(item.amount) }}</td>
                  </tr>

                  <tr class="total-row">
                      <td>三、营业利润（亏损以“-”号填列）</td><td class="center">20</td>
                      <td class="money">{{ formatMoney(reportData.net_profit) }}</td>
                  </tr>
                  <tr class="total-row">
                      <td>四、利润总额（亏损以“-”号填列）</td><td class="center">30</td>
                      <td class="money">{{ formatMoney(reportData.net_profit) }}</td>
                  </tr>
                  <tr class="total-row">
                      <td>五、净利润（净亏损以“-”号填列）</td><td class="center">40</td>
                      <td class="money">{{ formatMoney(reportData.net_profit) }}</td>
                  </tr>
              </tbody>
          </table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const companyName = ref('未来科技贸易有限公司')
const start = new Date(); start.setDate(1);
const today = new Date();
const dateRange = ref([start.toISOString().split('T')[0], today.toISOString().split('T')[0]])
const reportData = ref(null)

const incomes = computed(() => reportData.value ? reportData.value.rows.filter(r => r.type==='收入') : [])
const costs = computed(() => reportData.value ? reportData.value.rows.filter(r => r.type==='费用') : [])
const costsTotal = computed(() => reportData.value ? reportData.value.total_cost : 0)

const formatMoney = (val) => {
    if(val === 0) return '-'
    return Number(val).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}

const loadData = async () => {
    const res = await axios.post('/api/income_statement', {
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
/* 补充的样式 */
.report-paper {
    width: 210mm;
    margin: 20px auto;
    background: #fff;
    padding: 20mm;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.report-title {
    text-align: center; font-family: "SimSun"; font-size: 24px; margin-bottom: 20px;
}
.report-info {
    display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 10px; font-family: "SimSun";
}
.standard-table {
    width: 100%; border-collapse: collapse; border: 2px solid #000;
    font-family: "SimSun", serif; font-size: 14px;
}
.standard-table th, .standard-table td { border: 1px solid #000; padding: 8px; }
.standard-table th { background: #f8f8f8; text-align: center; }
.money { text-align: right; font-family: Arial; }
.center { text-align: center; }
.indent { padding-left: 2em; }
.section-header { font-weight: bold; }
.total-row { font-weight: bold; background-color: #fff; }
@media print {
    .no-print { display: none; }
    .report-paper { box-shadow: none; margin: 0; width: 100%; }
    .app-container { padding: 0; background: #fff; }
    .el-card { border: none; }
}
</style>