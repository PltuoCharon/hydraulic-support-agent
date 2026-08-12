// axios 实例: 统一 baseURL / 响应拆包 / 错误提示
import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/',          // /api 走 vite 代理到 127.0.0.1:8000
  timeout: 30000,
})

// 响应拦截: 后端统一格式 {code, data, msg}, code!==0 视为业务错误
http.interceptors.response.use(
  (resp) => {
    const body = resp.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code !== 0) {
        ElMessage.error(body.msg || '请求失败')
        return Promise.reject(new Error(body.msg))
      }
      return body.data        // 组件里直接拿 data
    }
    return body
  },
  (err) => {
    ElMessage.error('网络错误: ' + (err.message || 'unknown'))
    return Promise.reject(err)
  },
)

export const getAreas = (keyword = '') =>
  http.get('/api/areas/', { params: keyword ? { keyword } : {} })

export const getAreaDetail = (id) => http.get(`/api/areas/${id}/`)

export const postMatch = (payload) => http.post('/api/match/', payload)

export default http
