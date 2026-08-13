<script setup>
import { ref, watch, onMounted } from 'vue'
import { useChart } from '../composables/useChart'

const props = defineProps({ items: Array, required: Object })
const chartEl = ref(null)
const { setOption } = useChart(chartEl)

// 解析数值：区间文本 "1.27~1.31" 取中值，保证与参考线数值可比
function parseNum(v) {
  if (v == null || v === '') return null
  if (typeof v === 'number') return v
  const m = String(v).match(/(\d+(?:\.\d+)?)\s*[~～-]\s*(\d+(?:\.\d+)?)/)
  if (m) return (parseFloat(m[1]) + parseFloat(m[2])) / 2
  const n = parseFloat(String(v))
  return isNaN(n) ? null : n
}

function render() {
  if (!props.items.length) return
  const models = props.items.map(i => i.support_model)
  const res = props.items.map(i => parseNum(i.working_resistance) ?? 0)
  const ints = props.items.map(i => parseNum(i.intensity) ?? 0)
  const req = props.required || { resistance: 0, intensity: 0 }

  setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['工作阻力', '支护强度'] },
    grid: { left: 70, right: 60, bottom: 50 },
    xAxis: { type: 'category', data: models, axisLabel: { rotate: 30 } },
    yAxis: [
      { type: 'value', name: 'kN', axisLabel: { formatter: '{value}k' } },
      { type: 'value', name: 'MPa', min: 0 },
    ],
    series: [
      {
        name: '工作阻力', type: 'bar', barMaxWidth: 34,
        data: res,
        markLine: {
          symbol: 'none',
          lineStyle: { color: '#f56c6c', type: 'dashed', width: 2 },
          label: { formatter: `需求 ${req.resistance} kN`, position: 'insideEndTop' },
          data: [{ yAxis: req.resistance }],
        },
        itemStyle: { color: (p) => p.value < req.resistance ? '#f56c6c' : '#409eff' },
      },
      {
        name: '支护强度', type: 'bar', yAxisIndex: 1, barMaxWidth: 34,
        data: ints,
        markLine: {
          symbol: 'none',
          lineStyle: { color: '#e6a23c', type: 'dashed', width: 2 },
          label: { formatter: `需求 ${req.intensity} MPa`, position: 'insideEndTop' },
          data: [{ yAxis: req.intensity }],
        },
        itemStyle: { color: (p) => p.value < req.intensity ? '#f56c6c' : '#67c23a' },
      },
    ],
  })
}

onMounted(render)
// 需求值是异步拉取的，到达后重新渲染参考线
watch(() => [props.items, props.required], render, { deep: true })
</script>

<template>
  <div ref="chartEl" style="width: 100%; height: 320px" />
</template>
