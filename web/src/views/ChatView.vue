<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useChatStore } from '../store/chat'
import { streamChat, postMatch } from '../api'
import { useRouter } from 'vue-router'
import { marked } from 'marked'

const store = useChatStore()
const router = useRouter()
const lastMeta = ref(null)
const controller = ref(null)
const lastStage = ref('')
const input = ref('')
const sending = ref(false)
const listEl = ref(null)

// Markdown 渲染：marked 同步解析（流式渲染时对未闭合语法宽容）
const renderMd = (text) => {
  try { return marked.parse(text || '', { async: false }) }
  catch (e) { return (text || '').replace(/\n/g, '<br>') }
}

const scrollBottom = async () => {
  await nextTick()
  if (listEl.value) listEl.value.scrollTop = listEl.value.scrollHeight
}

const send = async () => {
  const text = input.value.trim()
  if (!text || sending.value) return
  store.pushUser(text)
  input.value = ''
  sending.value = true
  controller.value = new AbortController()
  const temp = { role: 'assistant', text: '' }
  store.messages.push(temp)
  scrollBottom()
  try {
    await streamChat(
      { message: text, session_id: store.sessionId },
      {
        onChunk: (c) => { temp.text += c; scrollBottom() },
        onMeta: (m) => { lastMeta.value = m; lastStage.value = m.stage || ''; if (m.session_id) store.setSession(m.session_id) },
        signal: controller.value.signal,
      }
    )
  } catch (e) {
    temp.text = '请求失败：' + (e.message || e)
  } finally {
    controller.value = null
    sending.value = false
    scrollBottom()
    if (lastMeta.value?.stage === 'explained') {
      const p = lastMeta.value.params || {}
      const t = { coal_thickness: Number(p.coal_thickness), dip_angle: Number(p.dip_angle) || 0, top_n: 3 }
      try {
        const r = await postMatch(t)
        store.pushCard({
          items: (r.items || []).map(it => ({
            model: it.support_model,
            similarity: Math.round((it.similarity ?? 0) * 100),
            resistance: it.working_resistance,
            intensity: it.intensity,
          })),
          total: r.total,
        })
        scrollBottom()
      } catch (e) { /* 卡片失败静默，不影响对话 */ }
    }
  }
}

onMounted(scrollBottom)
// 页面卸载时中止未完成的流式请求，避免泄漏/状态错乱
onBeforeUnmount(() => { if (controller.value) controller.value.abort() })
</script>
<template>
  <div class="chat-page">
    <div ref="listEl" class="chat-list">
      <div v-for="(m, i) in store.messages" :key="i" class="row" :class="m.role">
        <div class="bubble" :class="m.role">
          <span v-if="m.role === 'user'">{{ m.text }}</span>
          <div v-else-if="m.card" class="card-block">
            <div class="card-title">推荐结果（相似工况 {{ m.card.total }} 个）</div>
            <div v-for="(it, idx) in m.card.items" :key="it.model" class="rec-item">
              <b>#{{ idx + 1 }} {{ it.model }}</b>
              <span class="rec-sim">相似度 {{ it.similarity }}%</span>
              <span>{{ it.resistance != null ? it.resistance + ' kN' : '—' }}</span>
              <span>{{ it.intensity != null ? it.intensity + ' MPa' : '—' }}</span>
            </div>
            <el-button size="small" type="primary" style="margin-top: 8px"
                       @click="router.push('/result')">去结果页查看对比</el-button>
          </div>
          <div v-else class="assistant-text" v-html="renderMd(m.text)" />
        </div>
      </div>
    </div>

    <el-alert v-if="lastStage === 'confirm_pending'" type="warning" :closable="false"
              style="margin-bottom: 8px"
              title="参数已收集，请回复「对」确认，或直接改口补充（如：倾角是10度）" />

    <div class="input-bar">
      <el-input v-model="input" placeholder="输入工况或选型问题，Enter 发送"
                :disabled="sending" clearable
                @keyup.enter="send" />
      <el-button type="primary" :loading="sending"
                 :disabled="!input.trim() || sending" @click="send">发送</el-button>
      <el-button @click="store.clear()" :disabled="sending">清空</el-button>
    </div>
  </div>
</template>
<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
  min-height: 420px;
}
.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}
.row { display: flex; margin-bottom: 12px; }
.row.user { justify-content: flex-end; }
.row.assistant { justify-content: flex-start; }
.bubble {
  max-width: 72%;
  padding: 10px 14px;
  border-radius: 10px;
  line-height: 1.6;
  word-break: break-word;
}
.bubble.user {
  background: linear-gradient(120deg, #1f4a75, #16324f);
  color: #fff;
  border-top-right-radius: 2px;
}
.bubble.assistant {
  background: #fff;
  color: #303133;
  border-top-left-radius: 2px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .06);
}
.assistant-text {
  white-space: normal;
  font-family: inherit;
  margin: 0;
  line-height: 1.7;
}
.assistant-text :deep(p) { margin: 4px 0; }
.assistant-text :deep(ul), .assistant-text :deep(ol) { margin: 4px 0; padding-left: 20px; }
.assistant-text :deep(li) { margin: 2px 0; }
.assistant-text :deep(strong) { color: #303133; }
.assistant-text :deep(code) {
  background: #f5f5f5; padding: 1px 5px; border-radius: 3px;
  font-size: 0.92em; font-family: Consolas, Monaco, monospace;
}
.assistant-text :deep(pre) {
  background: #f6f8fa; padding: 10px; border-radius: 6px; overflow-x: auto;
  margin: 6px 0;
}

.card-block {
  background: #f0f7ff; border: 1px solid #d6e6ff; border-radius: 8px;
  padding: 10px 14px;
}
.card-title { font-weight: 600; color: #303133; margin-bottom: 6px; }
.rec-item {
  display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
  padding: 4px 0; border-bottom: 1px dashed #d6e6ff;
}
.rec-item:last-child { border-bottom: none; }
.rec-sim { color: #1f4a75; font-weight: 500; }
.input-bar {
  display: flex;
  gap: 8px;
  padding: 12px 0;
}
</style>
