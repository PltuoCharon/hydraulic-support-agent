<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMatchStore } from '../store/match'
import { useChart } from '../composables/useChart'
import { BRAND_COLORS } from '../utils/echarts'

const router = useRouter()
const store = useMatchStore()
const chartEl = ref(null)
const { setOption } = useChart(chartEl)

const selected = computed(() => store.compare)

// 解析数值：区间文本 "1.27~1.31" 取中值；纯数字直接用；解析失败返回 null
function parseNum(v) {
  if (v == null || v === '') return null
  if (typeof v === 'number') return v
  const m = String(v).match(/(\d+(?:\.\d+)?)\s*[~～-]\s*(\d+(?:\.\d+)?)/)
  if (m) return (parseFloat(m[1]) + parseFloat(m[2])) / 2
  const n = parseFloat(String(v))
  return isNaN(n) ? null : n
}

const DIMS = [
  { key: 'working_resistance', name: '工作阻力', unit: 'kN' },
  { key: 'intensity', name: '支护强度', unit: 'MPa' },
  { key: 'weight', name: '支架重量', unit: 't' },
  { key: 'height_max', name: '最大支撑高度', unit: 'm' },
  { key: 'initial_force', name: '初撑力', unit: 'kN' },
]

const missing = computed(() => {
  const list = []
  for (const it of selected.value) {
    const miss = DIMS.filter(d => parseNum(it[d.key]) == null).map(d => d.name)
    if (miss.length) list.push(`${it.support_model} 缺: ${miss.join('、')}（按 0 计）`)
  }
  return list
})

function render() {
  const sel = selected.value
  if (!sel.length) return
  const vals = sel.map(it => DIMS.map(d => parseNum(it[d.key]) ?? 0))
  const maxVals = DIMS.map((d, i) => Math.max(...vals.map(r => r[i]), 0.0001))
  const data = sel.map((it, r) => ({
    name: it.support_model,
    value: vals[r].map((v, i) => (v / maxVals[i]).toFixed(3)),
  }))
  setOption({
    color: BRAND_COLORS,
    legend: { data: data.map(d => d.name), bottom: 0 },
    radar: {
      indicator: DIMS.map(d => ({ name: `${d.name}(${d.unit})`, max: 1 })),
      radius: '62%',
    },
    series: [{
      type: 'radar', symbol: 'circle', symbolSize: 5,
      lineStyle: { width: 2 }, data,
    }],
  })
}

watch(selected, render, { deep: true })
onMounted(render)
</script>

<template>
  <h2>支架对比 · 雷达图</h2>

  <el-empty v-if="!selected.length" description="还没勾选支架，回结果页勾选 2~3 个再来">
    <el-button type="primary" @click="router.push('/result')">去结果页勾选</el-button>
  </el-empty>

  <template v-else>
    <el-alert v-if="missing.length" type="warning" :closable="false"
              :title="missing.join('；')" style="margin-bottom: 12px" />

    <el-card>
      <div ref="chartEl" style="width: 100%; height: 480px" />
    </el-card>

    <p style="color:#909399; margin-top: 8px">
      说明：各维度以所选支架中最大值为 1 归一化，仅用于形态对比；缺数据的维度按 0 计并在上方提示。
    </p>
  </template>
</template>
