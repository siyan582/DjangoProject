<template>
  <div class="home-container">
    <div class="welcome-header">
      <div class="left-content">
        <h2 class="company-name">{{ dashboardData.company_name }}</h2>
        <p class="subtitle">
          {{ currentDate }} | 欢迎回来，这是您的今日财务概览
        </p>
      </div>
      <div class="right-actions">
        <el-button type="primary" size="large" @click="$router.push('/voucher')">
          <el-icon style="margin-right:5px"><EditPen /></el-icon> 记一笔
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="cards-row">
      <el-col :span="6">
        <el-card shadow="hover" class="data-card card-blue">
          <div class="card-title">货币资金 (现金+银行)</div>
          <div class="card-number">
             ¥ <count-to :startVal="0" :endVal="Number(dashboardData.total_cash)" :duration="2000" />
          </div>
          <div class="card-footer">企业流动的血液</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="data-card card-green">
          <div class="card-title">应收账款 (债权)</div>
          <div class="card-number">
             ¥ <count-to :startVal="0" :endVal="Number(dashboardData.total_receivable)" :duration="2000" />
          </div>
          <div class="card-footer">待收回的货款</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="data-card card-red">
          <div class="card-title">应付账款 (债务)</div>
          <div class="card-number">
             ¥ <count-to :startVal="0" :endVal="Number(dashboardData.total_payable)" :duration="2000" />
          </div>
          <div class="card-footer">待支付的货款</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="data-card card-purple">
          <div class="card-title">本月销售额</div>
          <div class="card-number">
             ¥ <count-to :startVal="0" :endVal="Number(dashboardData.month_sales)" :duration="2000" />
          </div>
          <div class="card-footer">本月累计采购: ¥ {{ Number(dashboardData.month_purchase).toLocaleString() }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px; height: calc(100% - 220px);">
      <el-col :span="14">
        <el-card shadow="never" class="panel-card" style="height: 100%;">
          <template #header>
            <span class="panel-title"><el-icon><Menu /></el-icon> 常用功能快捷入口</span>
          </template>
          <div class="shortcut-grid">
            <div class="shortcut-item" @click="$router.push('/purchase_order')">
              <div class="icon-box bg-orange"><el-icon><ShoppingBag /></el-icon></div>
              <span>采购下单</span>
            </div>
            <div class="shortcut-item" @click="$router.push('/sales_order')">
              <div class="icon-box bg-blue"><el-icon><Sell /></el-icon></div>
              <span>销售开单</span>
            </div>
            <div class="shortcut-item" @click="$router.push('/collection')">
              <div class="icon-box bg-green"><el-icon><Wallet /></el-icon></div>
              <span>收款登记</span>
            </div>
            <div class="shortcut-item" @click="$router.push('/payment')">
              <div class="icon-box bg-red"><el-icon><CreditCard /></el-icon></div>
              <span>付款登记</span>
            </div>
            <div class="shortcut-item" @click="$router.push('/subject')">
              <div class="icon-box bg-cyan"><el-icon><Collection /></el-icon></div>
              <span>科目管理</span>
            </div>
            <div class="shortcut-item" @click="$router.push('/balance_sheet')">
              <div class="icon-box bg-purple"><el-icon><DataLine /></el-icon></div>
              <span>查看报表</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card shadow="never" class="panel-card" style="height: 100%; overflow-y: auto;">
          <template #header>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="panel-title"><el-icon><Timer /></el-icon> 最近账务动态</span>
                <el-button link type="primary" @click="$router.push('/voucher')">更多</el-button>
            </div>
          </template>

          <el-timeline style="padding-left: 10px;">
            <el-timeline-item
              v-for="(v, index) in dashboardData.recent_vouchers"
              :key="index"
              :timestamp="v.date"
              :type="index === 0 ? 'primary' : ''"
              :hollow="index === 0"
            >
              <div class="timeline-content">
                  <div class="t-summary">{{ v.summary }}</div>
                  <div class="t-info">
                      <el-tag size="small" type="info">{{ v.no }}</el-tag>
                      <span class="t-amount">¥ {{ Number(v.amount).toFixed(2) }}</span>
                  </div>
              </div>
            </el-timeline-item>
            <el-timeline-item v-if="dashboardData.recent_vouchers.length === 0" timestamp="现在">
                暂无凭证数据
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { EditPen, Menu, ShoppingBag, Sell, Wallet, CreditCard, Collection, DataLine, Timer } from '@element-plus/icons-vue'
// 简单的数字滚动组件实现（如果没有安装 vue-count-to，这里用简易版逻辑或直接显示数字）
// 为了保证你代码能直接跑，这里我们做一个简易的 CountTo 组件逻辑，
// 但因为是 setup 语法糖，直接用插值即可。如果想炫酷，可以安装 `vue3-count-to`。
// 这里我们直接用文本插值，简单粗暴不出错。

// 为了简单动画效果，我们定义一个本地组件（仅逻辑展示）
const CountTo = {
    props: ['endVal'],
    template: '<span>{{ Number(endVal).toLocaleString() }}</span>'
}

const dashboardData = ref({
    company_name: '加载中...',
    total_cash: 0,
    total_receivable: 0,
    total_payable: 0,
    month_sales: 0,
    month_purchase: 0,
    recent_vouchers: []
})

const currentDate = computed(() => {
    const d = new Date()
    return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日`
})

const loadStats = async () => {
    try {
        const res = await axios.get('/api/dashboard')
        if (res.data.code === 200) {
            dashboardData.value = res.data.data
        }
    } catch (e) {
        console.error("加载仪表盘失败", e)
    }
}

onMounted(() => {
    loadStats()
})
</script>

<style scoped>
.home-container {
    height: 100%;
    display: flex;
    flex-direction: column;
}

/* 顶部欢迎区 */
.welcome-header {
    background-color: #fff;
    padding: 20px 30px;
    border-radius: 8px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}
.company-name {
    margin: 0;
    font-size: 24px;
    color: #303133;
    font-weight: bold;
}
.subtitle {
    margin: 8px 0 0;
    color: #909399;
    font-size: 14px;
}

/* 卡片通用样式 */
.data-card {
    color: #fff;
    border: none;
    position: relative;
    overflow: hidden;
    cursor: default;
    transition: transform 0.3s;
}
.data-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.card-title {
    font-size: 14px;
    opacity: 0.9;
}
.card-number {
    font-size: 28px;
    font-weight: bold;
    margin: 10px 0;
    font-family: Consolas, sans-serif;
}
.card-footer {
    font-size: 12px;
    opacity: 0.8;
}

/* 卡片颜色渐变 */
.card-blue { background: linear-gradient(135deg, #409EFF, #79bbff); }
.card-green { background: linear-gradient(135deg, #67C23A, #95d475); }
.card-red { background: linear-gradient(135deg, #F56C6C, #f89898); }
.card-purple { background: linear-gradient(135deg, #a0cfff, #b37feb); }

/* 下方卡片 */
.panel-card {
    border-radius: 8px;
}
.panel-title {
    font-size: 16px;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* 快捷入口网格 */
.shortcut-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    padding: 10px;
}
.shortcut-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
}
.shortcut-item:hover {
    background-color: #ecf5ff;
    transform: scale(1.02);
}
.icon-box {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
    margin-bottom: 10px;
}
.shortcut-item span {
    font-size: 14px;
    color: #606266;
}

.bg-orange { background-color: #E6A23C; }
.bg-blue { background-color: #409EFF; }
.bg-green { background-color: #67C23A; }
.bg-red { background-color: #F56C6C; }
.bg-cyan { background-color: #00bcd4; }
.bg-purple { background-color: #9c27b0; }

/* 动态列表 */
.timeline-content {
    background: #f8f9fa;
    padding: 10px;
    border-radius: 4px;
}
.t-summary {
    font-size: 14px;
    color: #303133;
    margin-bottom: 5px;
    font-weight: 500;
}
.t-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.t-amount {
    font-weight: bold;
    color: #303133;
    font-family: Consolas;
}
</style>