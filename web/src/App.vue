<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AreaList from './components/AreaList.vue'
import { getAreas } from './api'

const title = ref('液压支架选型系统')
const showList = ref(true)
const selected = ref(null)
const areas = ref([])
const loading = ref(false)

const load = async () => {
  loading.value = true
  try {
    const data = await getAreas()
    // 适配: data 可能是数组, 也可能是 {items: [...]} 分页结构
    areas.value = Array.isArray(data) ? data : (data.items || [])
  } catch (e) {
    ElMessage.error('矿区列表加载失败，请确认后端已启动')
  } finally {
    loading.value = false
  }
}
onMounted(load)

const toggle = () => { showList.value = !showList.value }
const onSelect = (area) => { selected.value = area }
</script>

<template>
  <h1>{{ title }}</h1>
  <p>矿区数量：{{ areas.length }}</p>

  <el-button type="primary" @click="toggle">
    {{ showList ? '隐藏' : '显示' }}列表
  </el-button>
  <el-button @click="load">刷新</el-button>

  <div v-loading="loading">
    <AreaList :areas="areas" :show="showList" @select="onSelect" />
  </div>

  <el-alert v-if="selected" type="success" :closable="false"
            style="max-width: 600px; margin-top: 12px"
            :title="`已选中：${selected.area_name}（煤层 ${selected.coal_thickness}m）`" />
</template>
