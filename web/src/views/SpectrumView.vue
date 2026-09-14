<template>
  <div class="spectrum-page">
    <h2>架型谱系图</h2>
    <p class="note">
      X=工作阻力(kN)，Y=采高(m，区间中值)，点色=架型。
      本库 157 个 verified 型号的阻力/采高均来自公开型谱值，无轴相关估算点；
      控顶距、支护强度等字段的估算情况见各点 tooltip。
    </p>
    <div ref="chartRef" class="chart"></div>
    <footer class="foot">共 {{ total }} 个型号 · suspect 型号已排除 · 数据来源见各点 tooltip</footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getSpectrum } from '../api'

const chartRef = ref(null)
const total = ref(0)
let chart = null
const resize = () => chart && chart.resize()

onMounted(async () => {
  const items = (await getSpectrum()).items
  total.value = items.length
  const types = [...new Set(items.map(i => i.type || '未标注'))]
  const series = types.map(t => ({
    name: t,
    type: 'scatter',
    symbolSize: 10,
    emphasis: { focus: 'series' },
    data: items.filter(i => (i.type || '未标注') === t)
      .map(i => ({ value: [i.working_resistance, i.height_mid], raw: i }))
  }))
  chart = echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 70, right: 30, top: 50, bottom: 60 },
    legend: { top: 5 },
    tooltip: {
      trigger: 'item',
      formatter: p => {
        const r = p.data.raw
        return [`<b>${r.model}</b>`,
          `厂商: ${r.manufacturer || '未查到'}`,
          `阻力: ${r.working_resistance} kN`,
          `采高: ${r.height_min}~${r.height_max} m`,
          `估算字段: ${r.est_fields}`,
          `来源: ${r.source || '—'}`].join('<br/>')
      }
    },
    xAxis: { name: '工作阻力 (kN)', type: 'value' },
    yAxis: { name: '采高 (m)', type: 'value', min: 0 },
    series
  })
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart && chart.dispose()
})
</script>

<style scoped>
.spectrum-page { padding: 16px; }
.chart { width: 100%; height: 65vh; }
.note { color: #666; font-size: 13px; line-height: 1.6; }
.foot { color: #999; font-size: 12px; margin-top: 8px; }
</style>
