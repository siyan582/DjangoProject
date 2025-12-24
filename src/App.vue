<template>
  <el-config-provider :locale="zhCn">
    <div class="common-layout">
      <el-container class="layout-container">

        <el-aside width="200px" class="aside-menu">
          <div class="logo-area">
            <h3 style="color:white; margin:0; text-align:center; line-height:60px;">财务记账系统</h3>
          </div>

          <el-menu
            active-text-color="#409EFF"
            background-color="#304156"
            text-color="#bfcbd9"
            :default-active="$route.path"
            router
            class="el-menu-vertical"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon> <span>系统首页</span>
            </el-menu-item>

            <el-sub-menu index="1">
              <template #title><el-icon><Setting /></el-icon><span>基础资料</span></template>
              <el-menu-item index="/enterprise">企业信息管理</el-menu-item>
              <el-menu-item index="/subject">会计科目设置</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="2">
              <template #title><el-icon><ShoppingBag /></el-icon><span>采购管理</span></template>
              <el-menu-item index="/supplier">供应商管理</el-menu-item>
              <el-menu-item index="/purchase_order">采购订单</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="3">
              <template #title><el-icon><SoldOut /></el-icon><span>销售管理</span></template>
              <el-menu-item index="/customer">客户管理</el-menu-item>
              <el-menu-item index="/sales_order">销售订单</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="4">
              <template #title><el-icon><Wallet /></el-icon><span>资金与账务</span></template>
              <el-menu-item index="/voucher">会计分录(过账)</el-menu-item>
              <el-menu-item index="/payment">付款/支付</el-menu-item>
              <el-menu-item index="/collection">收款/回款</el-menu-item>
              <el-menu-item index="/report">期末对账</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="5">
              <template #title><el-icon><DataLine /></el-icon><span>财务报表</span></template>
              <el-menu-item index="/balance_sheet">资产负债表</el-menu-item>
              <el-menu-item index="/income_statement">利润表</el-menu-item>
              <el-menu-item index="/cash_flow">现金流量表</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-aside>

        <el-container style="position: relative;">
          <el-header class="header-bar">
            <div class="header-left"></div>

            <div class="header-right-fixed">
              <span class="user-text">当前用户：管理员（开放所有权限）</span>

            </div>
          </el-header>

          <el-main class="main-content">
            <router-view />
          </el-main>
        </el-container>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { House, Setting, ShoppingBag, SoldOut, Wallet, DataLine } from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
</script>

<style>
/* === 1. 全局重置 === */
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  background-color: #f0f2f5;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

/* === 2. 布局容器 === */
.common-layout,
.layout-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* 侧边栏 */
.aside-menu {
  background-color: #304156;
  color: white;
  height: 100%;
  overflow-x: hidden;
}

.logo-area {
  height: 60px;
  background-color: #2b3649;
}

.el-menu-vertical {
  border-right: none !important;
}

/* 顶栏 */
.header-bar {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  height: 60px;
  position: relative;
  width: 100%;
  box-sizing: border-box;
}

.header-right-fixed {
  position: fixed;
  right: 20px;
  top: 0;
  height: 60px;
  display: flex;
  align-items: center;
  z-index: 9999;
  background-color: transparent;
}

.user-text {
  font-size: 14px;
  color: #666;
  margin-right: 15px;
}

.logout-btn {
  font-size: 14px;
}

/* 内容区域 */
.main-content {
  background-color: #f0f2f5;
  padding: 20px !important;
  height: calc(100vh - 60px);
  overflow-y: auto;
  box-sizing: border-box;
}

.el-main {
  --el-main-padding: 0 !important;
}

.app-container {
  width: 100%;
}

/* ==================================================
   新增：全局打印样式
   作用：当点击打印时，隐藏菜单、顶栏，只显示报表内容
================================================== */
@media print {
  /* 1. 隐藏侧边栏、顶栏、以及带有 .no-print 类的元素 */
  .el-aside,
  .el-header,
  .aside-menu,
  .header-bar,
  .no-print {
    display: none !important;
  }

  /* 2. 调整主容器，去掉滚动条，让内容自动延伸 */
  .common-layout,
  .layout-container,
  .el-container,
  .main-content {
    height: auto !important;
    width: 100% !important;
    overflow: visible !important;
    background-color: white !important; /* 打印时强制白底 */
    margin: 0 !important;
    padding: 0 !important;
    position: static !important;
  }

  /* 3. 隐藏 Element Plus 可能残留的边框 */
  .el-card {
    border: none !important;
    box-shadow: none !important;
  }

  /* 4. 强制页面设置为 A4 纸张大小（部分浏览器支持） */
  @page {
    size: A4;
    margin: 10mm; /* 设置页边距，防止内容被切掉 */
  }
}
</style>