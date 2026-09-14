<template>
  <div class="vendor-page">
    <h2>厂商分布图</h2>
    <p class="note">
      verified 型号 {{ total }} 个，其中厂商字段已填 {{ known }} 个（覆盖率 {{ coverage }}%），
      <b>未知 {{ unknown }} 个</b>。"国产"为采集期占位值，非实际厂商，待回溯。
    </p>
    <div ref="chartRef" class="chart"></div>
    <footer class="foot">suspect 型号已排除 · 覆盖率口径: known / total = {{ known }}/{{ total }}</footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getVendors } from '../api'

const chartRef = ref(null)
const total = ref(0)
const known = ref(0)
const unknown = ref(0)
const coverage = ref(0)
let chart = null
const resize = () => chart && chart.resize()

onMounted(async () => {
  const d = await getVendors()
  total.value = d.total
  known.value = d.known
  unknown.value = d.unknown
  coverage.value = d.coverage
  const items = d.items
  chart = echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 130, right: 60, top: 30, bottom: 40 },
    tooltip: {
      trigger: 'item',
      formatter: p => `${p.name}: ${p.value} 个型号` +
        (p.name === '未知' ? '<br/>厂商字段为空, 待来源回溯补录' :
         p.name === '国产' ? '<br/>占位值, 非实际厂商, 待回溯' : '')
    },
    xAxis: { type: 'value', name: '型号数' },
    yAxis: { type: 'category', data: items.map(i => i.manufacturer), inverse: true },
    series: [{
      type: 'bar',
      data: items.map(i => ({
        value: i.cnt,
        itemStyle: i.manufacturer === '未知'
          ? { color: '#c0c4cc', borderType: 'dashed', borderColor: '#909399' }
          : i.manufacturer === '国产' ? { color: '#e6a23c' } : {}
      })),
      label: { show: true, position: 'right' },
      barMaxWidth: 28
    }]
  })
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart && chart.dispose()
})
</script>

<style scoped>
.vendor-page { padding: 16px; }
.chart { width: 100%; height: 55vh; }
.note { color: #666; font-size: 13px; line-height: 1.6; }
.foot { color: #999; font-size: 12px; margin-top: 8px; }
</style>
