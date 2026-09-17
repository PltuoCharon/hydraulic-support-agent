<template>
  <div class="hs-page">

    <PageHeader
      eyebrow="Spatial Overview"
      title="矿区地图"
      description="按区域查看已建立近似坐标的矿区与工作面，并可直接将矿区工况带入智能选型。"
    >
      <StatusBadge
        label="城市级近似坐标"
        status="warning"
      />
    </PageHeader>


    <section class="map-metrics">

      <MetricCard
        label="可用矿区"
        :value="availableAreas"
        note="不含盲测数据"
        status="success"
      />

      <MetricCard
        label="可地图化"
        :value="areas.length"
        note="同时具备经纬度"
        status="success"
      />

      <MetricCard
        label="坐标覆盖率"
        :value="coordinateCoverage"
        unit="%"
        note="区域展示覆盖情况"
        status="warning"
      />

    </section>


    <section class="map-workspace">

      <div
        ref="chartRef"
        class="map-chart"
      />


      <aside
        v-loading="panelLoading"
        class="detail-panel"
      >

        <template v-if="selected">

          <div class="detail-head">

            <div>
              <span class="detail-label">
                当前矿区
              </span>

              <h3>
                {{ selected.area_name }}
              </h3>
            </div>

            <el-tag
              v-if="selected.category"
              size="small"
              effect="plain"
            >
              {{ selected.category }}
            </el-tag>

          </div>


          <div class="detail-grid">

            <div>
              <span>煤层厚度</span>
              <strong>
                {{ selected.coal_thickness ?? '—' }}
                <small>m</small>
              </strong>
            </div>

            <div>
              <span>煤层倾角</span>
              <strong>
                {{ selected.dip_angle ?? '—' }}
                <small>°</small>
              </strong>
            </div>

            <div>
              <span>埋深</span>
              <strong>
                {{ selected.depth ?? '—' }}
                <small>m</small>
              </strong>
            </div>

            <div>
              <span>煤层硬度 f</span>
              <strong>
                {{ selected.hardness_f ?? '—' }}
              </strong>
            </div>

          </div>


          <div class="detail-lines">

            <p>
              <span>顶板</span>
              {{ selected.roof_category || '—' }}
            </p>

            <p>
              <span>矿压</span>
              {{ selected.mine_pressure || '—' }}
            </p>

            <p>
              <span>瓦斯</span>
              {{ selected.gas_level || '—' }}
            </p>

          </div>


          <DataCompleteness
            :filled="selectedFilledCount"
            :total="CONDITION_FIELDS.length"
          />


          <el-divider />


          <div class="supports-head">
            <strong>
              在用支架型号
            </strong>

            <span>
              {{ groupedSupports.length }}
            </span>
          </div>


          <ul
            v-if="groupedSupports.length"
            class="support-list"
          >
            <li
              v-for="s in groupedSupports"
              :key="s.model"
            >
              <div>
                <strong>
                  {{ s.model }}
                </strong>

                <span>
                  {{ s.working_resistance }}
                  kN
                </span>
              </div>

              <small v-if="s.n > 1">
                {{ s.n }} 条案例
              </small>
            </li>
          </ul>


          <EmptyState
            v-else
            title="没有在用支架记录"
            description="该矿区当前没有关联到可展示的 verified 支架型号。"
          />


          <el-button
            type="primary"
            class="recommend-button"
            @click="recommend"
          >
            以该矿区工况进入选型
          </el-button>

        </template>


        <EmptyState
          v-else
          title="请选择地图中的矿区"
          description="点击蓝色点位后，这里会显示完整工况、字段完整度以及关联的在用支架。"
        />

      </aside>

    </section>


    <div class="coordinate-note">
      <strong>坐标口径：</strong>
      {{ coordNote || '坐标为地级市近似位置' }}。
      仅用于区域分布展示，不代表矿井精确位置。
      地图边界数据已本地化，可离线使用。
    </div>

  </div>
</template>


<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
} from 'vue'

import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import * as echarts from 'echarts'

import {
  getAreaDetail,
  getAreaSupports,
  getMapAreas,
  getStats,
} from '../api'

import { useMatchStore } from '../store/match'

import PageHeader from '../components/ui/PageHeader.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'
import DataCompleteness from '../components/ui/DataCompleteness.vue'
import EmptyState from '../components/ui/EmptyState.vue'


const router = useRouter()
const store = useMatchStore()

const chartRef = ref(null)

const areas = ref([])
const selected = ref(null)
const supports = ref([])

const availableAreas = ref(0)
const coordNote = ref('')

const panelLoading = ref(false)


const CONDITION_FIELDS = [
  'coal_thickness',
  'dip_angle',
  'hardness_f',
  'roof_category',
  'floor_pressure',
  'mine_pressure',
  'gas_level',
  'depth',
  'face_length',
]


const hasValue = (value) => {
  if (
    value === null
    || value === undefined
  ) {
    return false
  }

  if (typeof value === 'string') {
    return value.trim() !== ''
  }

  return true
}


const coordinateCoverage = computed(() => {
  if (!availableAreas.value) {
    return 0
  }

  return Number(
    (
      areas.value.length
      / availableAreas.value
      * 100
    ).toFixed(1)
  )
})


const selectedFilledCount = computed(() => {
  if (!selected.value) {
    return 0
  }

  return CONDITION_FIELDS.filter(
    (field) =>
      hasValue(selected.value[field])
  ).length
})


const groupedSupports = computed(() => {
  const m = new Map()

  for (const s of supports.value) {
    if (!m.has(s.model)) {
      m.set(
        s.model,
        {
          ...s,
          n: 0,
        }
      )
    }

    m.get(s.model).n += 1
  }

  return [...m.values()]
})


let chart = null


const onResize = () => {
  if (chart) {
    chart.resize()
  }
}


async function onSelect(area) {
  panelLoading.value = true

  try {
    const [
      detail,
      supportData,
    ] = await Promise.all([
      getAreaDetail(area.id),
      getAreaSupports(area.id),
    ])

    selected.value = detail || area

    supports.value =
      supportData?.items || []
  } catch {
    selected.value = area
    supports.value = []

    ElMessage.warning(
      '矿区详情加载不完整，当前显示地图基础数据'
    )
  } finally {
    panelLoading.value = false
  }
}


function recommend() {
  if (!selected.value) {
    return
  }

  store.prefillFromArea(
    selected.value
  )

  router.push({
    path: '/select',
    query: {
      tab: 'form',
    },
  })
}


onMounted(async () => {
  try {
    const [
      geo,
      mapData,
      stats,
    ] = await Promise.all([
      fetch('/geo/china.json')
        .then((r) => r.json()),

      getMapAreas(),

      getStats(),
    ])

    echarts.registerMap(
      'china',
      geo
    )

    areas.value =
      mapData?.items || []

    coordNote.value =
      mapData?.coord_note || ''

    availableAreas.value =
      stats?.areas || 0


    chart = echarts.init(
      chartRef.value
    )


    chart.setOption({

      geo: {
        map: 'china',

        roam: true,

        scaleLimit: {
          min: 0.8,
          max: 5,
        },

        label: {
          show: false,
        },

        itemStyle: {
          areaColor: '#f2f5f8',
          borderColor: '#b7c4d2',
          borderWidth: 0.8,
        },

        emphasis: {
          itemStyle: {
            areaColor: '#e4edf6',
          },

          label: {
            show: false,
          },
        },
      },


      tooltip: {
        trigger: 'item',

        backgroundColor:
          'rgba(18, 43, 66, 0.94)',

        borderWidth: 0,

        textStyle: {
          color: '#fff',
          fontSize: 12,
        },

        formatter: (p) => {
          const a =
            p.data?.area

          if (!a) {
            return p.name
          }

          return (
            `<b>${a.area_name}</b>`
            + '<br/>'
            + `类别：${a.category || '—'}`
            + '<br/>'
            + `煤层厚度：${a.coal_thickness ?? '—'} m`
            + '<br/>'
            + `倾角：${a.dip_angle ?? '—'}°`
            + '<br/>'
            + '<span style="opacity:.68">'
            + '点击查看完整工况'
            + '</span>'
          )
        },
      },


      series: [
        {
          name: '矿区',

          type: 'scatter',

          coordinateSystem: 'geo',

          data: areas.value.map(
            (a) => ({
              name: a.area_name,

              value: [
                a.lng,
                a.lat,
              ],

              area: a,
            })
          ),

          symbolSize: 10,

          itemStyle: {
            color: '#2f80ed',
            borderColor: '#ffffff',
            borderWidth: 1.5,

            shadowBlur: 6,

            shadowColor:
              'rgba(47,128,237,.25)',
          },

          emphasis: {
            scale: 1.5,

            itemStyle: {
              color: '#f3a93b',
            },
          },

          zlevel: 2,
        },
      ],

    })


    chart.on(
      'click',
      (p) => {
        if (p.data?.area) {
          onSelect(p.data.area)
        }
      }
    )


    window.addEventListener(
      'resize',
      onResize
    )

  } catch {
    ElMessage.error(
      '矿区地图加载失败，请检查后端与本地地图数据'
    )
  }
})


onBeforeUnmount(() => {
  window.removeEventListener(
    'resize',
    onResize
  )

  if (chart) {
    chart.dispose()
  }
})
</script>


<style scoped>
.map-metrics {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 220px));
  gap: 12px;

  margin-bottom: 16px;
}


.map-workspace {
  display: grid;
  grid-template-columns:
    minmax(0, 1fr)
    350px;

  overflow: hidden;

  min-height: 560px;
  height: calc(100vh - 270px);
  max-height: 760px;

  background: #fff;

  border: 1px solid var(--hs-gray-200);
  border-radius: var(--hs-radius-lg);
}


.map-chart {
  width: 100%;
  min-width: 0;
  height: 100%;

  background:
    linear-gradient(
      180deg,
      #fbfcfd,
      #f6f8fa
    );
}


.detail-panel {
  overflow-y: auto;

  padding: 18px;

  background: #fff;

  border-left:
    1px solid var(--hs-gray-200);
}


.detail-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;

  margin-bottom: 16px;
}


.detail-label {
  color: var(--hs-gray-500);

  font-size: 10px;
}


.detail-head h3 {
  margin: 3px 0 0;

  color: var(--hs-navy-900);

  font-size: 17px;
}


.detail-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));

  margin-bottom: 14px;

  border-top:
    1px solid var(--hs-gray-100);
  border-left:
    1px solid var(--hs-gray-100);
}


.detail-grid > div {
  padding: 10px;

  border-right:
    1px solid var(--hs-gray-100);
  border-bottom:
    1px solid var(--hs-gray-100);
}


.detail-grid span {
  display: block;

  color: var(--hs-gray-500);

  font-size: 10px;
}


.detail-grid strong {
  display: block;

  margin-top: 3px;

  color: var(--hs-gray-950);

  font-size: 14px;
}


.detail-grid small {
  color: var(--hs-gray-500);

  font-size: 10px;
  font-weight: 500;
}


.detail-lines {
  margin-bottom: 14px;
}


.detail-lines p {
  display: flex;

  margin: 5px 0;

  color: var(--hs-gray-700);

  font-size: 11px;
  line-height: 1.5;
}


.detail-lines span {
  flex: 0 0 42px;

  color: var(--hs-gray-500);
}


.supports-head {
  display: flex;
  align-items: center;
  justify-content: space-between;

  margin-bottom: 9px;
}


.supports-head strong {
  color: var(--hs-gray-950);

  font-size: 13px;
}


.supports-head span {
  color: var(--hs-gray-500);

  font-size: 11px;
}


.support-list {
  margin: 0;
  padding: 0;

  list-style: none;
}


.support-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;

  padding: 8px 0;

  border-bottom:
    1px solid var(--hs-gray-100);
}


.support-list li div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}


.support-list strong {
  color: var(--hs-gray-800);

  font-size: 11px;
}


.support-list span,
.support-list small {
  color: var(--hs-gray-500);

  font-size: 10px;
}


.recommend-button {
  width: 100%;

  margin-top: 17px;
}


.coordinate-note {
  margin-top: 10px;

  color: var(--hs-gray-500);

  font-size: 11px;
  line-height: 1.6;
}


.coordinate-note strong {
  color: var(--hs-gray-700);
}


@media (max-width: 1366px) {
  .map-workspace {
    grid-template-columns:
      minmax(0, 1fr)
      310px;
  }

  .map-metrics {
    grid-template-columns:
      repeat(3, minmax(0, 1fr));
  }
}
</style>
