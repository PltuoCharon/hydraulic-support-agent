<script setup>
import { ref, onMounted } from 'vue'
import { useChart } from '../composables/useChart'
const chartEl = ref(null)
const { setOption } = useChart(chartEl)
onMounted(() => {
  setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['工作阻力(kN)', '支护强度(MPa)'] },
    xAxis: { type: 'category', data: ['ZY12000/28/58', 'ZY21000/38/82D', 'ZF15000/25/45'] },
    yAxis: [
      { type: 'value', name: 'kN' },
      { type: 'value', name: 'MPa' },
    ],
    series: [
      { name: '工作阻力(kN)', type: 'bar', barMaxWidth: 34, data: [12000, 21000, 15000] },
      { name: '支护强度(MPa)', type: 'bar', yAxisIndex: 1, barMaxWidth: 34, data: [1.29, 1.45, 1.46] },
    ],
  })
})
</script>
<template>
  <h2>支架对比</h2>
  <el-card>
    <div ref="chartEl" style="width: 100%; height: 360px" />
  </el-card>
  <p style="color:#909399; margin-top:8px">D2 封装自检：D3 将替换为雷达图（5 维归一化叠加对比）</p>
</template>
