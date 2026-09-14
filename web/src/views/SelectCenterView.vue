<template>
  <div class="select-center">
    <el-tabs v-model="active" class="tabs">
      <el-tab-pane label="表单输入" name="form">
        <InputView />
      </el-tab-pane>
      <el-tab-pane label="选型向导" name="wizard" lazy>
        <WizardView />
      </el-tab-pane>
      <el-tab-pane label="对话选型" name="chat" lazy>
        <ChatView />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
// W30-D4: 三入口Tab整合。表单页签不lazy(矿区预填依赖其onMounted读store);
// 向导/对话lazy, 不激活不初始化(ChatView有自己的session逻辑)。
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import InputView from './InputView.vue'
import WizardView from './WizardView.vue'
import ChatView from './ChatView.vue'

const route = useRoute()
const active = ref(['form', 'wizard', 'chat'].includes(route.query.tab) ? route.query.tab : 'form')
</script>

<style scoped>
.select-center { padding: 0 16px 16px; }
</style>
