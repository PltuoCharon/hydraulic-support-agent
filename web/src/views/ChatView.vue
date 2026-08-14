<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useChatStore } from '../store/chat'
import { streamChat } from '../api'

const store = useChatStore()
const input = ref('')
const sending = ref(false)
const listEl = ref(null)

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
          <pre v-else class="assistant-text">{{ m.text }}</pre>
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
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0;
}
.input-bar {
  display: flex;
  gap: 8px;
  padding: 12px 0;
}
</style>
