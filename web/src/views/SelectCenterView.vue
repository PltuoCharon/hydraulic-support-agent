<template>
  <div class="select-center">
    <div v-if="st" class="stats-bar">
      <div class="stat" @click="$router.push('/spectrum')"><b>{{ st.supports }}</b><span>支架型号 · 含2条存疑已隔离</span></div>
      <div class="stat" @click="$router.push('/map')"><b>{{ st.areas }}</b><span>在用矿区 · 不含盲测集</span></div>
      <div class="stat" @click="$router.push('/areas')"><b>{{ st.cases }}</b><span>工况案例</span></div>
      <div class="stat plain"><b>{{ st.intensity_coverage }}%</b><span>支护强度覆盖率</span></div>
      <div class="stat plain"><b>{{ st.weight_coverage }}%</b><span>重量覆盖率(偏低待补录)</span></div>
    </div>
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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import InputView from './InputView.vue'
import WizardView from './WizardView.vue'
import ChatView from './ChatView.vue'
import { getStats } from '../api'

const route = useRoute()
const active = ref(['form', 'wizard', 'chat'].includes(route.query.tab) ? route.query.tab : 'form')
const st = ref(null)
onMounted(async () => { st.value = await getStats() })
</script>

<style scoped>
.select-center { padding: 0 16px 16px; }
.stats-bar { display: flex; gap: 16px; margin: 14px 0 4px; }
.stat { flex: 1; background: #fff; border: 1px solid #ebeef5; border-radius: 8px; padding: 12px; text-align: center; cursor: pointer; }
.stat.plain { cursor: default; }
.stat b { font-size: 22px; display: block; color: #1f2d3d; }
.stat span { font-size: 12px; color: #909399; }
</style>
