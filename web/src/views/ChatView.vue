<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useChatStore } from '../store/chat'
import { streamChat } from '../api'
import { marked } from 'marked'

const store = useChatStore()
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
  const temp = { role: 'assistant', text: '' }
  store.messages.push(temp)
  scrollBottom()
  try {
    await streamChat(
      { message: text, session_id: store.sessionId },
      {
        onChunk: (c) => { temp.text += c; scrollBottom() },
        onMeta: (m) => { if (m.session_id) store.setSession(m.session_id) },
      }
    )
  } catch (e) {
    temp.text = '请求失败：' + (e.message || e)
  } finally {
    sending.value = false
    scrollBottom()
  }
}

onMounted(scrollBottom)
</script>
<template>
  <div class="chat-page">
    <div ref="listEl" class="chat-list">
      <div v-for="(m, i) in store.messages" :key="i" class="row" :class="m.role">
        <div class="bubble" :class="m.role">
          <span v-if="m.role === 'user'">{{ m.text }}</span>
          <div v-else class="assistant-text" v-html="renderMd(m.text)" />
        </div>
      </div>
    </div>

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
  background: #409eff;
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
.input-bar {
  display: flex;
  gap: 8px;
  padding: 12px 0;
}
</style>
