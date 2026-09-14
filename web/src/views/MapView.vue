<template>
  <div class="map-page">
    <div ref="chartRef" class="map-chart"></div>
    <footer class="coord-note">
      坐标为地级市近似位置 · 地图边界数据已本地化（/geo/china.json），离线可用 · 共 {{ areas.length }} 个矿区
    </footer>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts'
import { getMapAreas } from '../api'

const emit = defineEmits(['select'])   // 点击矿区→父组件信息卡(D6)
const chartRef = ref(null)
const areas = ref([])
let chart = null
const onResize = () => chart && chart.resize()

onMounted(async () => {
  // GeoJSON 本地加载: 断网可渲染(W29验收项)
  const geo = await fetch('/geo/china.json').then(r => r.json())
  echarts.registerMap('china', geo)
  areas.value = (await getMapAreas()).items

  chart = echarts.init(chartRef.value)
  chart.setOption({
    geo: {
      map: 'china', roam: true, scaleLimit: { min: 0.8, max: 5 },
      label: { show: false },
      itemStyle: { areaColor: '#f3f6fa', borderColor: '#b8c4d4' },
      emphasis: { itemStyle: { areaColor: '#e8f0fe' }, label: { show: false } },
    },
    tooltip: {
      trigger: 'item',
      formatter: (p) => {
        const a = p.data && p.data.area
        if (!a) return p.name
        return `<b>${a.area_name}</b><br/>类别: ${a.category || '—'}<br/>` +
               `煤厚: ${a.coal_thickness ?? '—'}m · 倾角: ${a.dip_angle ?? '—'}°<br/>` +
               `<span style="color:#909399">点击选择该矿区</span>`
      },
    },
    series: [{
      name: '矿区', type: 'effectScatter', coordinateSystem: 'geo',
      data: areas.value.map(a => ({ name: a.area_name, value: [a.lng, a.lat], area: a })),
      symbolSize: 10,
      rippleEffect: { brushType: 'stroke', scale: 3 },
      itemStyle: { color: '#c0392b', shadowBlur: 6, shadowColor: 'rgba(192,57,43,.4)' },
      emphasis: { scale: 1.6 },
      zlevel: 2,
    }],
  })
  chart.on('click', (p) => { if (p.data && p.data.area) emit('select', p.data.area) })
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chart && chart.dispose()
})
</script>

<style scoped>
.map-page { display: flex; flex-direction: column; height: 100%; }
.map-chart { flex: 1; min-height: 560px; }
.coord-note { padding: 8px 16px; color: #909399; font-size: 12px; border-top: 1px solid #ebeef5; }
</style>
