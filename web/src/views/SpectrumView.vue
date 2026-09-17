<template>
  <div class="hs-page spectrum-page">
    <PageHeader
      eyebrow="Model Spectrum"
      title="架型谱系"
      description="查看 verified 液压支架在工作阻力与支撑高度范围上的分布，并按基础架型进行筛选。"
    >
      <StatusBadge
        :label="`${total} 个 verified 型号`"
        status="info"
      />
    </PageHeader>

    <section class="metric-grid">
      <MetricCard
        label="数据库总型号"
        :value="quality?.supports?.total ?? '—'"
        note="包含 verified 与 suspect"
      />

      <MetricCard
        label="参与谱系分析"
        :value="total"
        note="仅 verified 型号"
      />

      <MetricCard
        label="Suspect"
        :value="quality?.supports?.suspect ?? '—'"
        note="默认排除"
      />

      <MetricCard
        label="架型已标注"
        :value="typeMetric?.known ?? '—'"
        :note="typeMetric ? `${typeMetric.coverage}% 字段覆盖率` : '—'"
      />
    </section>

    <section class="engineering-panel">
      <div class="panel-head">
        <div>
          <h3>工作阻力 × 支撑高度分布</h3>
          <p>
            原始细分架型仅在 tooltip 中保留；
            图表按基础架型归并展示，不修改数据库原始值。
          </p>
        </div>

        <el-radio-group
          v-model="activeType"
          size="small"
        >
          <el-radio-button
            v-for="item in filters"
            :key="item.name"
            :value="item.name"
          >
            {{ item.name }} · {{ item.count }}
          </el-radio-button>
        </el-radio-group>
      </div>

      <el-alert
        v-if="axisNote"
        :title="axisNote"
        type="info"
        :closable="false"
        show-icon
        class="axis-note"
      />

      <div
        ref="chartRef"
        class="spectrum-chart"
      />

      <div class="chart-foot">
        <span>X：工作阻力 / kN</span>
        <span>Y：支撑高度区间中值 / m</span>
        <span>点色：基础架型</span>
        <span>suspect 型号不参与分析</span>
      </div>
    </section>
  </div>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from 'vue'
import * as echarts from 'echarts'

import {
  getDataQuality,
  getSpectrum,
} from '../api'

import PageHeader from '../components/ui/PageHeader.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'


const chartRef = ref(null)

const items = ref([])
const total = ref(0)
const axisNote = ref('')
const quality = ref(null)
const activeType = ref('全部')
const error = ref('')

let chart = null


const baseType = (raw) => {
  if (!raw) return '未标注'

  if (raw.startsWith('支撑掩护式')) {
    return '支撑掩护式'
  }

  if (raw.startsWith('支撑式')) {
    return '支撑式'
  }

  if (raw.includes('放顶煤')) {
    return '放顶煤'
  }

  if (raw.startsWith('掩护式')) {
    return '掩护式'
  }

  return '其他'
}


const typeMetric = computed(() =>
  quality.value?.supports?.verified_fields
    ?.find(i => i.key === 'type')
)


const groupedCounts = computed(() => {
  const result = {
    掩护式: 0,
    支撑掩护式: 0,
    支撑式: 0,
    放顶煤: 0,
    其他: 0,
    未标注: 0,
  }

  for (const item of items.value) {
    result[baseType(item.type)] += 1
  }

  return result
})


const filters = computed(() => [
  {
    name: '全部',
    count: items.value.length,
  },
  ...Object.entries(groupedCounts.value)
    .filter(([, count]) => count > 0)
    .map(([name, count]) => ({
      name,
      count,
    })),
])


const visibleItems = computed(() => {
  if (activeType.value === '全部') {
    return items.value
  }

  return items.value.filter(
    i => baseType(i.type) === activeType.value,
  )
})


const typeColors = {
  掩护式: '#2F80ED',
  支撑掩护式: '#123B61',
  支撑式: '#6B7280',
  放顶煤: '#F3A93B',
  其他: '#8B5CF6',
  未标注: '#B8C0CC',
}


const escapeHtml = (value) =>
  String(value ?? '—')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')


const renderChart = () => {
  if (!chartRef.value) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const categories = [
    '掩护式',
    '支撑掩护式',
    '支撑式',
    '放顶煤',
    '其他',
    '未标注',
  ]

  const series = categories
    .map(category => ({
      name: category,
      type: 'scatter',
      symbolSize: 9,
      itemStyle: {
        color: typeColors[category],
      },
      emphasis: {
        scale: 1.6,
      },
      data: visibleItems.value
        .filter(
          item => baseType(item.type) === category,
        )
        .map(item => ({
          value: [
            item.working_resistance,
            item.height_mid,
          ],
          raw: item,
        })),
    }))
    .filter(s => s.data.length > 0)

  chart.setOption({
    animationDuration: 350,

    grid: {
      left: 72,
      right: 32,
      top: 34,
      bottom: 62,
    },

    legend: {
      show: false,
    },

    tooltip: {
      trigger: 'item',
      confine: true,
      formatter: (p) => {
        const r = p.data.raw

        return [
          `<b>${escapeHtml(r.model)}</b>`,
          `基础架型：${escapeHtml(baseType(r.type))}`,
          `原始架型：${escapeHtml(r.type || '未标注')}`,
          `制造商：${escapeHtml(r.manufacturer || '未查到')}`,
          `工作阻力：${escapeHtml(r.working_resistance)} kN`,
          `支撑高度：${escapeHtml(r.height_min)} ~ ${escapeHtml(r.height_max)} m`,
          `估算标记：${escapeHtml(r.est_fields || '无')}`,
          `来源：${escapeHtml(r.source || '—')}`,
        ].join('<br>')
      },
    },

    xAxis: {
      type: 'value',
      name: '工作阻力 / kN',
      nameLocation: 'middle',
      nameGap: 38,
      splitLine: {
        lineStyle: {
          color: '#E9EDF2',
        },
      },
    },

    yAxis: {
      type: 'value',
      min: 0,
      name: '支撑高度区间中值 / m',
      nameLocation: 'middle',
      nameGap: 48,
      splitLine: {
        lineStyle: {
          color: '#E9EDF2',
        },
      },
    },

    series,
  }, true)
}


const resize = () => {
  chart?.resize()
}


onMounted(async () => {
  try {
    const [
      spectrum,
      qualityData,
    ] = await Promise.all([
      getSpectrum(),
      getDataQuality(),
    ])

    items.value = spectrum.items || []
    total.value = spectrum.total || items.value.length
    axisNote.value = spectrum.axis_note || ''
    quality.value = qualityData

    await nextTick()
    renderChart()

    window.addEventListener(
      'resize',
      resize,
    )
  } catch (e) {
    error.value = '谱系数据加载失败'
  }
})


watch(
  activeType,
  async () => {
    await nextTick()
    renderChart()
  },
)


onBeforeUnmount(() => {
  window.removeEventListener(
    'resize',
    resize,
  )

  chart?.dispose()
})
</script>

<style scoped>
.spectrum-page {
  display: grid;
  gap: 18px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.engineering-panel {
  padding: 20px;
  background: #fff;
  border: 1px solid var(--hs-gray-200, #e5e7eb);
  border-radius: var(--hs-radius-lg, 10px);
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 22px;
  margin-bottom: 14px;
}

.panel-head h3 {
  margin: 0 0 6px;
  font-size: 17px;
}

.panel-head p {
  margin: 0;
  color: #667085;
  font-size: 13px;
  line-height: 1.6;
}

.axis-note {
  margin-bottom: 14px;
}

.spectrum-chart {
  width: 100%;
  height: 560px;
}

.chart-foot {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 24px;
  padding-top: 12px;
  border-top: 1px solid #eef1f4;
  color: #667085;
  font-size: 12px;
}

@media (max-width: 1200px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .panel-head {
    display: grid;
  }
}
</style>
