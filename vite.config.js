import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // --- 新增以下 server 配置 ---
  server: {
    proxy: {
      // 这里的配置意味着：在本地开发时，所有请求 /api 的操作都会被转发到 8000 端口
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // 如果你的 Django 接口里已经包含了 /api 前缀，则不需要 rewrite
        // 如果 Django 里没有 /api 前缀，请取消下面这行的注释：
        // rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
  // --- 新增结束 ---
})