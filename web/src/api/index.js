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

export const getRequirement = (thickness) =>
  http.get('/api/requirement/', { params: { coal_thickness: thickness } })

export const postRecalc = (payload) => http.post('/api/recalc/', payload)

export const postChat = (message) => http.post('/api/chat/', { message })

export const streamChat = ({ message, session_id }, { onChunk, onMeta }) => {
  const base = 'http://127.0.0.1:8000'   // 直连后端；vite 代理对原生 fetch 的 SSE 流支持不保险
  return new Promise((resolve, reject) => {
    fetch(`${base}/api/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id, stream: true }),
    }).then(resp => {
      if (!resp.ok) { reject(new Error('HTTP ' + resp.status)); return }
      const reader = resp.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buf = ''
      let finished = false
      const pump = () => {
        if (finished) return
        reader.read().then(({ done, value }) => {
          if (done) { resolve(); return }
          buf += decoder.decode(value, { stream: true })
          let idx
          while ((idx = buf.indexOf('\n\n')) >= 0) {
            const raw = buf.slice(0, idx)
            buf = buf.slice(idx + 2)
            for (const line of raw.split('\n')) {
              if (line.startsWith('data: ')) {
                const payload = line.slice(6)
                if (payload === '[DONE]') { finished = true; resolve(); return }
                try {
                  const obj = JSON.parse(payload)
                  if (obj.chunk != null) onChunk(obj.chunk)
                  if (obj.session_id) onMeta && onMeta(obj)
                } catch (e) { /* 忽略非 JSON 行 */ }
              }
            }
            if (finished) return
          }
          pump()
        }).catch(reject)
      }
      pump()
    }).catch(reject)
  })
}

export default http
