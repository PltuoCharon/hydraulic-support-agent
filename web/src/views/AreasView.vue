<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getAreas } from '../api'
import { useMatchStore } from '../store/match'

const router = useRouter()
const store = useMatchStore()

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

// 选中 → 工况字段入 store → 跳表单页(用户可再修改)
const onSelect = (area) => {
  selected.value = area
  store.prefillFromArea(area)
}

const goFill = () => router.push('/input')
</script>

<template>
  <h2>矿区选择</h2>
  <p>共 {{ areas.length }} 个矿区，点击卡片选中，自动带出工况参数</p>
  <el-button @click="load" style="margin-bottom: 12px">刷新</el-button>

  <div v-loading="loading" class="grid">
    <el-card v-for="a in areas" :key="a.id"
             :class="['area-card', { active: selected?.id === a.id }]"
             shadow="hover" @click="onSelect(a)">
      <template #header>
        <b>{{ a.area_name }}</b>
        <el-tag v-if="a.category" size="small" style="margin-left: 8px">{{ a.category }}</el-tag>
      </template>
      <p>煤层厚度：{{ a.coal_thickness ?? '—' }} m</p>
      <p>倾角：{{ a.dip_angle ?? '—' }}° ｜ 埋深：{{ a.depth ?? '—' }} m</p>
      <p v-if="a.mining_height_min || a.mining_height_max">
        采高：{{ a.mining_height_min ?? '?' }}~{{ a.mining_height_max ?? '?' }} m
      </p>
      <p v-if="a.gas_level">瓦斯：{{ a.gas_level }}</p>
    </el-card>
  </div>

  <el-alert v-if="selected" type="success" :closable="false" style="margin-top: 16px"
            :title="`已选中：${selected.area_name}（煤层 ${selected.coal_thickness}m，倾角 ${selected.dip_angle}°）`">
    <el-button type="primary" size="small" style="margin-top: 8px" @click="goFill">
      带参数去匹配 →
    </el-button>
  </el-alert>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}
.area-card { cursor: pointer; }
.area-card.active { border: 2px solid #409eff; }
</style>
