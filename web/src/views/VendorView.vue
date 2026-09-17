<template>
  <div class="hs-page vendor-page">
    <PageHeader
      eyebrow="Manufacturer Coverage"
      title="制造商分析"
      description="区分制造商字段完整度与已知制造商分布；缺失数据不作为制造商类别参与比较。"
    >
      <StatusBadge
        label="仅分析 verified 型号"
        status="info"
      />
    </PageHeader>

    <section class="metric-grid">
      <MetricCard
        label="Verified 型号"
        :value="data.total"
        note="suspect 默认排除"
      />

      <MetricCard
        label="制造商已核实"
        :value="data.usable_known"
        note="具有明确制造商值"
      />

      <MetricCard
        label="制造商缺失"
        :value="data.unknown"
        note="继续来源回溯"
      />

      <MetricCard
        label="字段覆盖率"
        :value="`${data.usable_coverage}%`"
        note="已核实 / verified"
      />
    </section>

    <section class="coverage-panel">
      <div class="coverage-head">
        <div>
          <h3>制造商字段完整度</h3>
          <p>
            {{ data.usable_known }} / {{ data.total }}
            个 verified 型号已核实制造商。
          </p>
        </div>

        <strong>
          {{ data.usable_coverage }}%
        </strong>
      </div>

      <el-progress
        :percentage="data.usable_coverage"
        :stroke-width="10"
      />
    </section>

    <section class="engineering-panel">
      <div class="panel-head">
        <div>
          <h3>已知制造商分布</h3>
          <p>
            只统计制造商字段已核实的
            {{ data.usable_known }} 个型号。
            本图反映数据库样本分布，不代表市场份额。
          </p>
        </div>

        <StatusBadge
          :label="`未知 ${data.unknown} 条已排除`"
          status="warning"
        />
      </div>

      <div
        ref="chartRef"
        class="vendor-chart"
      />

      <el-alert
        title="制造商数量差异同时受到数据库采集范围影响，不能直接解释为企业市场占有率。"
        type="warning"
        :closable="false"
        show-icon
      />
    </section>
  </div>
</template>

<script setup>
import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
} from 'vue'
import * as echarts from 'echarts'

import { getVendors } from '../api'

import PageHeader from '../components/ui/PageHeader.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'


const chartRef = ref(null)

const data = reactive({
  total: 0,
  unknown: 0,
  usable_known: 0,
  usable_coverage: 0,
  known_items: [],
})

let chart = null


const renderChart = () => {
  if (!chartRef.value) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const items = [...data.known_items]
    .sort((a, b) => b.cnt - a.cnt)

  chart.setOption({
    animationDuration: 350,

    grid: {
      left: 210,
      right: 70,
      top: 20,
      bottom: 45,
    },

    tooltip: {
      trigger: 'item',
      formatter: p =>
        `${p.name}<br>数据库中已核实型号：${p.value} 个`,
    },

    xAxis: {
      type: 'value',
      name: '型号数',
      minInterval: 1,
      splitLine: {
        lineStyle: {
          color: '#E9EDF2',
        },
      },
    },

    yAxis: {
      type: 'category',
      inverse: true,
      data: items.map(
        i => i.manufacturer,
      ),
      axisLabel: {
        width: 185,
        overflow: 'truncate',
      },
    },

    series: [
      {
        type: 'bar',
        barMaxWidth: 24,
        data: items.map(i => i.cnt),
        itemStyle: {
          color: '#2F80ED',
          borderRadius: [0, 3, 3, 0],
        },
        label: {
          show: true,
          position: 'right',
        },
      },
    ],
  }, true)
}


const resize = () => {
  chart?.resize()
}


onMounted(async () => {
  const result = await getVendors()

  Object.assign(
    data,
    result,
  )

  await nextTick()
  renderChart()

  window.addEventListener(
    'resize',
    resize,
  )
})


onBeforeUnmount(() => {
  window.removeEventListener(
    'resize',
    resize,
  )

  chart?.dispose()
})
</script>

<style scoped>
.vendor-page {
  display: grid;
  gap: 18px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.coverage-panel,
.engineering-panel {
  padding: 20px;
  background: #fff;
  border: 1px solid var(--hs-gray-200, #e5e7eb);
  border-radius: var(--hs-radius-lg, 10px);
}

.coverage-head,
.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 15px;
}

.coverage-head h3,
.panel-head h3 {
  margin: 0 0 6px;
  font-size: 17px;
}

.coverage-head p,
.panel-head p {
  margin: 0;
  color: #667085;
  font-size: 13px;
  line-height: 1.6;
}

.coverage-head strong {
  color: #123B61;
  font-size: 28px;
}

.vendor-chart {
  width: 100%;
  height: 430px;
  margin-bottom: 14px;
}

@media (max-width: 1200px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
