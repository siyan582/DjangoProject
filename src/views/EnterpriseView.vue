<template>
  <div class="app-container">
    <el-card class="enterprise-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="title-icon"><OfficeBuilding /></el-icon>
            <span class="title-text">企业基本信息管理 (UC001)</span>
          </div>
          <el-button type="primary" size="default" @click="saveData" :loading="loading">
            <el-icon style="margin-right: 6px"><Check /></el-icon> 保存配置
          </el-button>
        </div>
      </template>

      <div class="form-wrapper">
        <el-form :model="form" label-width="110px" size="large">

          <el-form-item label="企业名称">
            <el-input
              v-model="form.name"
              placeholder="请输入营业执照上的完整名称"
              prefix-icon="School"
              clearable
            />
          </el-form-item>

          <el-row :gutter="60">
            <el-col :span="12">
              <el-form-item label="企业类型">
                <el-select v-model="form.type" placeholder="请选择企业类型" style="width: 100%">
                  <el-option label="有限责任公司" value="有限责任公司" />
                  <el-option label="股份有限公司" value="股份有限公司" />
                  <el-option label="个人独资企业" value="个人独资企业" />
                  <el-option label="合伙企业" value="合伙企业" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="税务登记号">
                <el-input
                    v-model="form.tax_no"
                    placeholder="请输入统一社会信用代码"
                    prefix-icon="Postcard"
                    clearable
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="60">
            <el-col :span="12">
              <el-form-item label="注册资金">
                <el-input-number
                    v-model="form.registered_capital"
                    :min="0"
                    :precision="0"
                    controls-position="right"
                    style="width: 100%"
                />
                <span class="suffix-text">元 (RMB)</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="成立日期">
                <el-date-picker
                    v-model="form.establish_date"
                    type="date"
                    placeholder="选择营业执照日期"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                    :prefix-icon="Calendar"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="所属行业">
            <el-input
                v-model="form.industry"
                placeholder="例如：互联网 / 软件开发 / 电子商务"
                prefix-icon="DataLine"
                clearable
            />
          </el-form-item>

        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import axios from 'axios'
import {ElMessage} from 'element-plus'
// 引入精美的图标
import {OfficeBuilding, Check, School, Postcard, Calendar, DataLine} from '@element-plus/icons-vue'

const loading = ref(false)
const form = ref({
  name: '',
  type: '',
  registered_capital: 0,
  establish_date: '',
  industry: '',
  tax_no: ''
})

const loadData = async () => {
  try {
    const res = await axios.get('/api/enterprise')
    if (res.data.data) {
      form.value = res.data.data
    }
  } catch (error) {
    console.error("加载失败", error)
  }
}

const saveData = async () => {
  loading.value = true
  try {
    const res = await axios.post('/api/enterprise', form.value)
    if (res.data.code === 200) {
      ElMessage.success('企业信息保存成功！')
    } else {
      ElMessage.error('保存失败：' + res.data.message)
    }
  } catch (error) {
    ElMessage.error('连接服务器失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.app-container {
  width: 100%;
}

.enterprise-card {
  width: 100%;
  border-radius: 8px; /* 圆角稍微大一点，更现代 */
}

/* 头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0; /* 微调垂直内边距 */
}

.header-left {
  display: flex;
  align-items: center;
}

.title-icon {
  font-size: 20px;
  color: #409EFF; /* Element Plus 主题蓝 */
  margin-right: 10px;
  background: #ecf5ff; /* 浅蓝背景 */
  padding: 6px;
  border-radius: 6px;
}

.title-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 表单区域样式 */
.form-wrapper {
  padding: 20px 40px; /* 增加左右留白，让表单在宽屏下更聚焦 */
  max-width: 1200px; /* 限制一下最大内容宽度，防止在超宽屏上输入框拉得太长太长 */
  margin: 0 auto; /* 居中显示表单内容 */
}

.suffix-text {
  margin-left: 10px;
  font-size: 14px;
  color: #909399;
}
</style>