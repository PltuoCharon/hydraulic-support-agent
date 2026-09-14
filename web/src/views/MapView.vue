<template>
  <div class="map-page">
    <div class="map-body">
      <div ref="chartRef" class="map-chart"></div>
      <aside v-if="selected" class="info-card">
        <h3>{{ selected.area_name }}</h3>
        <p><span>类别</span>{{ selected.category || '—' }}</p>
        <p><span>煤厚</span>{{ selected.coal_thickness ?? '—' }} m</p>
        <p><span>倾角</span>{{ selected.dip_angle ?? '—' }} °</p>
        <p><span>采高</span>{{ selected.mining_height_min ?? '—' }} ~ {{ selected.mining_height_max ?? '—' }} m</p>
        <el-divider />
        <h4>在用支架（{{ supports.length }}）</h4>
        <ul class="sup-list">
          <li v-for="s in supports" :key="s.id">{{ s.model }} · {{ s.working_resistance }} kN</li>
          <li v-if="!supports.length" class="empty">无在用支架记录</li>
        </ul>
        <el-button type="primary" style="width:100%" @click="recommend">
          以该矿区工况发起推荐
        </el-button>
      </aside>
    </div>
    <footer class="coord-note">
      坐标为地级市近似位置 · 地图边界数据已本地化（/geo/china.json），离线可用 · 共 {{ areas.length }} 个矿区
    </footer>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getMapAreas, getAreaSupports } from '../api'
import { useMatchStore } from '../store/match'

const router = useRouter()
const store = useMatchStore()
const chartRef = ref(null)
const areas = ref([])
const selected = ref(null)
const supports = ref([])
let chart = null
const onResize = () => chart && chart.resize()

async function onSelect(a) {
  selected.value = a
  supports.value = (await getAreaSupports(a.id)).items
}

function recommend() {
  store.prefillFromArea(selected.value)   // 复用 W25 矿区路径既有链路
  router.push('/select')
}

onMounted(async () => {
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
  chart.on('click', (p) => { if (p.data && p.data.area) onSelect(p.data.area) })
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chart && chart.dispose()
})
</script>

<style scoped>
.map-page { display: flex; flex-direction: column; height: 100%; }
.map-body { flex: 1; display: flex; min-height: 0; }
.map-chart { flex: 1; min-height: 560px; }
.info-card { width: 320px; flex-shrink: 0; padding: 16px; border-left: 1px solid #ebeef5; overflow-y: auto; }
.info-card h3 { margin: 0 0 12px; }
.info-card p { margin: 6px 0; font-size: 14px; }
.info-card p span { display: inline-block; width: 48px; color: #909399; }
.info-card h4 { margin: 0 0 8px; font-size: 14px; }
.sup-list { margin: 0 0 16px; padding-left: 18px; font-size: 13px; }
.sup-list .empty { color: #909399; list-style: none; margin-left: -18px; }
.coord-note { padding: 8px 16px; color: #909399; font-size: 12px; border-top: 1px solid #ebeef5; }
</style>
