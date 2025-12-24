import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus' // 引入 Element Plus
import 'element-plus/dist/index.css' // 引入它的样式文件

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus) // 告诉 Vue 使用它

app.mount('#app')
