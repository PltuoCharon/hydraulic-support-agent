<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { getAreas } from '../api'
import { useMatchStore } from '../store/match'

import PageHeader from '../components/ui/PageHeader.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'
import DataCompleteness from '../components/ui/DataCompleteness.vue'
import EmptyState from '../components/ui/EmptyState.vue'


const router = useRouter()
const store = useMatchStore()

const areas = ref([])
const keyword = ref('')
const loading = ref(false)
const selected = ref(null)


const CONDITION_FIELDS = [
  ['coal_thickness', '煤层厚度'],
  ['dip_angle', '煤层倾角'],
  ['hardness_f', '煤层硬度'],
  ['roof_category', '顶板类型'],
  ['floor_pressure', '底板比压'],
  ['mine_pressure', '矿压特征'],
  ['gas_level', '瓦斯'],
  ['depth', '埋深'],
  ['face_length', '工作面长度'],
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


const filtered = computed(() => {
  const q = keyword.value.trim()

  if (!q) {
    return areas.value
  }

  return areas.value.filter(
    (a) =>
      (a.area_name || a.name || '')
        .includes(q)
  )
})


const mappableCount = computed(
  () => areas.value.filter(
    (a) =>
      a.lng !== null
      && a.lng !== undefined
      && a.lat !== null
      && a.lat !== undefined
  ).length
)


const coordinateCoverage = computed(() => {
  if (!areas.value.length) {
    return 0
  }

  return (
    mappableCount.value
    / areas.value.length
    * 100
  ).toFixed(1)
})


const miningHeightCount = computed(
  () => areas.value.filter(
    (a) =>
      hasValue(a.mining_height_min)
      || hasValue(a.mining_height_max)
  ).length
)


const sourceCount = computed(
  () => areas.value.filter(
    (a) => hasValue(a.source)
  ).length
)


const filledCount = (area) => {
  return CONDITION_FIELDS.filter(
    ([field]) => hasValue(area[field])
  ).length
}


const missingLabels = (area) => {
  return CONDITION_FIELDS
    .filter(
      ([field]) => !hasValue(area[field])
    )
    .map(([, label]) => label)
}


const load = async () => {
  loading.value = true

  try {
    const data = await getAreas()

    areas.value = Array.isArray(data)
      ? data
      : (data.items || [])
  } catch {
    ElMessage.error(
      '矿区列表加载失败，请确认后端已启动'
    )
  } finally {
    loading.value = false
  }
}


const onSelect = (area) => {
  selected.value = area
  store.prefillFromArea(area)
}


const goArea = (area) => {
  store.prefillFromArea(area)

  router.push({
    path: '/select',
    query: {
      tab: 'form',
    },
  })
}


onMounted(load)
</script>


<template>
  <div class="hs-page">

    <PageHeader
      eyebrow="Mining Conditions"
      title="矿区工况"
      description="浏览已纳入数据库的矿区与工作面工况。盲测数据不会出现在前台列表中。"
    >
      <el-button @click="load">
        刷新数据
      </el-button>
    </PageHeader>


    <section class="area-metrics">

      <MetricCard
        label="可用矿区"
        :value="areas.length"
        note="不含盲测数据"
        status="success"
      />

      <MetricCard
        label="可地图化"
        :value="mappableCount"
        :note="`坐标覆盖率 ${coordinateCoverage}%`"
        status="success"
      />

      <MetricCard
        label="来源已记录"
        :value="sourceCount"
        :note="`共 ${areas.length} 条记录`"
        status="success"
      />

      <MetricCard
        label="采高范围覆盖"
        :value="miningHeightCount"
        :note="`共 ${areas.length} 条记录`"
        status="warning"
      />

    </section>


    <el-alert
      class="completeness-note"
      type="info"
      :closable="false"
      show-icon
    >
      “关键工况字段完整度”仅统计 9 项工况字段是否有值，
      不代表数据准确性或工程可信度。
      采高范围当前单独统计，不纳入完整度分母。
    </el-alert>


    <section class="toolbar">

      <div>
        <strong>
          矿区记录
        </strong>

        <span>
          显示 {{ filtered.length }}
          / {{ areas.length }}
        </span>
      </div>

      <el-input
        v-model="keyword"
        clearable
        placeholder="搜索矿区或工作面名称"
        style="max-width: 320px"
      />

    </section>


    <EmptyState
      v-if="!loading && areas.length === 0"
      title="暂无矿区数据"
      description="请确认后端数据服务已经启动，然后重新加载。"
    >
      <el-button
        type="primary"
        @click="load"
      >
        重新加载
      </el-button>
    </EmptyState>


    <div
      v-loading="loading"
      class="area-grid"
    >

      <article
        v-for="a in filtered"
        :key="a.id"
        class="area-card"
        :class="{
          active:
            selected?.id === a.id,
        }"
        @click="onSelect(a)"
      >

        <header class="area-card-head">

          <div>
            <h3>
              {{ a.area_name }}
            </h3>

            <span class="area-id">
              ID {{ a.id }}
            </span>
          </div>

          <div class="head-badges">
            <el-tag
              v-if="a.category"
              size="small"
              effect="plain"
            >
              {{ a.category }}
            </el-tag>

            <StatusBadge
              v-if="a.source"
              label="来源已记录"
              status="info"
            />

            <StatusBadge
              v-else
              label="来源缺失"
              status="warning"
            />
          </div>

        </header>


        <div class="parameter-grid">

          <div>
            <span>煤层厚度</span>
            <strong>
              {{ a.coal_thickness ?? '—' }}
              <small>m</small>
            </strong>
          </div>

          <div>
            <span>煤层倾角</span>
            <strong>
              {{ a.dip_angle ?? '—' }}
              <small>°</small>
            </strong>
          </div>

          <div>
            <span>埋深</span>
            <strong>
              {{ a.depth ?? '—' }}
              <small>m</small>
            </strong>
          </div>

          <div>
            <span>煤层硬度 f</span>
            <strong>
              {{ a.hardness_f ?? '—' }}
            </strong>
          </div>

        </div>


        <div class="condition-lines">

          <p>
            <span>顶板</span>
            {{ a.roof_category || '—' }}
          </p>

          <p>
            <span>瓦斯</span>
            {{ a.gas_level || '—' }}
          </p>

        </div>


        <DataCompleteness
          compact
          :filled="filledCount(a)"
          :total="CONDITION_FIELDS.length"
        />


        <p
          v-if="missingLabels(a).length"
          class="missing-fields"
        >
          缺失：
          {{ missingLabels(a).join('、') }}
        </p>


        <footer class="area-card-footer">

          <span
            v-if="
              a.lng !== null
              && a.lng !== undefined
              && a.lat !== null
              && a.lat !== undefined
            "
            class="coordinate-ok"
          >
            ● 可地图化
          </span>

          <span
            v-else
            class="coordinate-missing"
          >
            ○ 坐标缺失
          </span>

          <el-button
            type="primary"
            link
            @click.stop="goArea(a)"
          >
            带工况进入选型 →
          </el-button>

        </footer>

      </article>

    </div>

  </div>
</template>


<style scoped>
.area-metrics {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(0, 1fr));
  gap: 12px;

  margin-bottom: 16px;
}


.completeness-note {
  margin-bottom: 18px;
}


.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  margin-bottom: 14px;
}


.toolbar strong {
  color: var(--hs-gray-950);

  font-size: 15px;
}


.toolbar span {
  margin-left: 9px;

  color: var(--hs-gray-500);

  font-size: 12px;
}


.area-grid {
  display: grid;
  grid-template-columns:
    repeat(
      auto-fill,
      minmax(320px, 1fr)
    );
  gap: 14px;
}


.area-card {
  padding: 17px;

  background: #fff;

  border: 1px solid var(--hs-gray-200);
  border-radius: var(--hs-radius-lg);

  cursor: pointer;

  transition:
    border-color var(--hs-transition),
    box-shadow var(--hs-transition);
}


.area-card:hover {
  border-color: #bfd5e8;

  box-shadow: var(--hs-shadow-sm);
}


.area-card.active {
  border-color: var(--hs-blue-600);

  box-shadow:
    0 0 0 2px
    rgba(47, 128, 237, 0.08);
}


.area-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;

  margin-bottom: 15px;
}


.area-card h3 {
  margin: 0;

  color: var(--hs-navy-900);

  font-size: 15px;
}


.area-id {
  display: block;

  margin-top: 3px;

  color: var(--hs-gray-500);

  font-size: 10px;
}


.head-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 5px;
}


.parameter-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));

  margin-bottom: 12px;

  border-top: 1px solid var(--hs-gray-100);
  border-left: 1px solid var(--hs-gray-100);
}


.parameter-grid > div {
  padding: 10px;

  border-right: 1px solid var(--hs-gray-100);
  border-bottom: 1px solid var(--hs-gray-100);
}


.parameter-grid span {
  display: block;

  margin-bottom: 3px;

  color: var(--hs-gray-500);

  font-size: 10px;
}


.parameter-grid strong {
  color: var(--hs-gray-950);

  font-size: 14px;
}


.parameter-grid small {
  color: var(--hs-gray-500);

  font-size: 10px;
  font-weight: 500;
}


.condition-lines {
  margin-bottom: 13px;
}


.condition-lines p {
  display: flex;

  margin: 4px 0;

  color: var(--hs-gray-700);

  font-size: 11px;
  line-height: 1.55;
}


.condition-lines span {
  flex: 0 0 42px;

  color: var(--hs-gray-500);
}


.missing-fields {
  margin: 8px 0 0;

  color: var(--hs-gray-500);

  font-size: 10px;
  line-height: 1.5;
}


.area-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;

  margin-top: 14px;
  padding-top: 11px;

  border-top: 1px solid var(--hs-gray-100);
}


.coordinate-ok,
.coordinate-missing {
  font-size: 10px;
}


.coordinate-ok {
  color: var(--hs-green-600);
}


.coordinate-missing {
  color: var(--hs-gray-500);
}


@media (max-width: 1366px) {
  .area-metrics {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }
}
</style>
