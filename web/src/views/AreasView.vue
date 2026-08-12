<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AreaList from '../components/AreaList.vue'
import { getAreas } from '../api'

const areas = ref([])
const loading = ref(false)
const selected = ref(null)

const load = async () => {
  loading.value = true
  try {
    const data = await getAreas()
    areas.value = Array.isArray(data) ? data : (data.items || [])
  } catch (e) {
    ElMessage.error('矿区列表加载失败，请确认后端已启动')
  } finally {
    loading.value = false
  }
}
onMounted(load)

// D5: 选中后拉工况条件回填表单
const onSelect = (area) => { selected.value = area }
</script>

<template>
  <h2>矿区选择</h2>
  <p>共 {{ areas.length }} 个矿区，点击卡片/行选中</p>
  <el-button @click="load">刷新</el-button>
  <div v-loading="loading">
    <AreaList :areas="areas" :show="true" @select="onSelect" />
  </div>
  <el-alert v-if="selected" type="success" :closable="false"
            style="max-width: 600px; margin-top: 12px"
            :title="`已选中：${selected.area_name}`" />
</template>
