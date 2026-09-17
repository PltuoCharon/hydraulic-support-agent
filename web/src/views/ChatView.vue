<template>
  <div class="chat-compat-page">
    <el-alert
      type="info"
      :closable="false"
      show-icon
      title="对话选型页面继续保留兼容；也可以从任意页面右下角打开全局工程助手。"
    />

    <AgentConversation
      context-label="智能选型 · 对话选型"
    />
  </div>
</template>


<script setup>
import AgentConversation
  from '../components/AgentConversation.vue'
</script>


<style scoped>
.chat-compat-page {
  display: flex;
  flex-direction: column;
  gap: 10px;

  min-height:
    calc(100vh - 260px);
}
</style>
