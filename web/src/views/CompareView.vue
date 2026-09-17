<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMatchStore } from '../store/match'
import { useChart } from '../composables/useChart'
import { BRAND_COLORS } from '../utils/echarts'
import { badge } from '../utils/badge'

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
    const miss = DIMS
      .filter(
        d => parseNum(it[d.key]) == null
      )
      .map(d => d.name)

    if (miss.length) {
      list.push(
        `${it.support_model} 缺：${miss.join('、')}`
      )
    }
  }

  return list
})


const comparableDims = computed(() => {
  if (!selected.value.length) {
    return []
  }

  return DIMS.filter(
    dim =>
      selected.value.every(
        item =>
          parseNum(
            item[dim.key]
          ) != null
      )
  )
})


const excludedDims = computed(() =>
  DIMS.filter(
    dim =>
      !comparableDims.value
        .some(
          item =>
            item.key === dim.key
        )
  )
)


function render() {
  const sel = selected.value
  const dims = comparableDims.value

  if (
    !sel.length
    || dims.length < 3
  ) {
    return
  }

  const vals = sel.map(
    item =>
      dims.map(
        dim =>
          parseNum(
            item[dim.key]
          )
      )
  )

  const maxVals = dims.map(
    (dim, index) =>
      Math.max(
        ...vals.map(
          row => row[index]
        ),
        0.0001,
      )
  )

  const data = sel.map(
    (item, rowIndex) => ({
      name: item.support_model,

      value:
        vals[rowIndex]
          .map(
            (value, index) =>
              Number(
                (
                  value
                  / maxVals[index]
                ).toFixed(3)
              )
          ),
    })
  )

  setOption({
    color: BRAND_COLORS,

    legend: {
      data:
        data.map(d => d.name),

      bottom: 0,
    },

    radar: {
      indicator:
        dims.map(dim => ({
          name:
            `${dim.name}(${dim.unit})`,

          max: 1,
        })),

      radius: '62%',
    },

    series: [
      {
        type: 'radar',
        symbol: 'circle',
        symbolSize: 5,

        lineStyle: {
          width: 2,
        },

        data,
      },
    ],
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
      <el-empty
        v-if="comparableDims.length < 3"
        description="共同完整维度不足 3 项，暂不绘制雷达图"
      />

      <div
        v-show="comparableDims.length >= 3"
        ref="chartEl"
        style="width: 100%; height: 480px"
      />
    </el-card>

    <div class="badge-row" style="margin-top: 12px; display: flex; gap: 16px; flex-wrap: wrap">
      <span v-for="it in selected" :key="it.support_model" style="display: inline-flex; align-items: center">
        {{ it.support_model }}
        <el-tooltip :content="badge(it).tip" placement="top">
          <el-tag :type="badge(it).type" size="small" effect="plain" style="margin-left: 6px">{{ badge(it).text }}</el-tag>
        </el-tooltip>
      </span>
    </div>
    <p style="color:#909399; margin-top: 8px">
      说明：雷达图仅使用所有已选型号均有值的共同完整维度，
      并以所选支架中该维度最大值为 1 归一化。
      缺失字段不会按 0 参与计算。
    </p>

    <p style="color:#909399; margin-top: 4px">
      当前纳入：
      {{
        comparableDims.length
          ? comparableDims.map(d => d.name).join('、')
          : '无'
      }}
      ；
      排除：
      {{
        excludedDims.length
          ? excludedDims.map(d => d.name).join('、')
          : '无'
      }}。
    </p>
  </template>
</template>
