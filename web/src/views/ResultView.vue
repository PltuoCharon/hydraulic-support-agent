<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMatchStore } from '../store/match'
import { getRequirement } from '../api'
import CompareBar from '../components/CompareBar.vue'

const router = useRouter()
const store = useMatchStore()

const items = computed(() => store.result?.items || [])
const cond = computed(() => store.conditions)

// 需求值自治：进入结果页时若还没有则自己拉（不依赖输入页改动）
onMounted(async () => {
  if (!store.required && store.conditions?.coal_thickness) {
    try {
      const req = await getRequirement(store.conditions.coal_thickness)
      store.setRequired(req || null)
    } catch (e) { /* 静默 */ }
  }
})

const simPct = (s) => Math.round((s ?? 0) * 100)
const simType = (s) => (s ?? 0) >= 0.7 ? 'success' : (s ?? 0) >= 0.5 ? 'warning' : ''

const paramRows = (it) => [
  { k: '工作阻力', v: it.working_resistance != null ? it.working_resistance + ' kN' : '—' },
  { k: '支护强度', v: it.intensity != null ? it.intensity + ' MPa' : '未查到公开参数' },
  { k: '支架高度', v: it.height_min != null && it.height_max != null ? `${it.height_min}~${it.height_max} m` : '—' },
  { k: '支架重量', v: it.weight != null ? it.weight + ' t' : '—' },
  { k: '中心距',   v: it.center_dist != null ? it.center_dist + ' m' : '—' },
  { k: '初撑力',   v: it.initial_force != null ? it.initial_force + ' kN' : '—' },
]
</script>

<template>
  <h2>推荐结果</h2>

  <el-card v-if="items.length" style="margin-bottom: 16px">
    <template #header><b>Top-N 参数对比</b></template>
    <CompareBar :items="items" :required="store.required" />
  </el-card>

  <el-empty v-if="!store.result" description="还没有匹配结果">
    <el-button type="primary" @click="router.push('/input')">去输入工况</el-button>
  </el-empty>

  <template v-else>
    <el-descriptions :column="3" border style="margin-bottom: 16px">
      <el-descriptions-item label="煤层厚度">{{ cond.coal_thickness }} m</el-descriptions-item>
      <el-descriptions-item label="煤层倾角">{{ cond.dip_angle }}°</el-descriptions-item>
      <el-descriptions-item label="候选数">{{ store.result.total }}</el-descriptions-item>
    </el-descriptions>

    <el-alert v-if="store.compare.length > 0" type="info" :closable="false"
              style="margin-bottom: 12px"
              :title="`已选 ${store.compare.length}/3 个支架用于对比`">
      <template #default>
        <el-button size="small" type="primary" @click="router.push('/compare')">对比雷达图 →</el-button>
        <el-button size="small" @click="store.clearCompare()">清空</el-button>
      </template>
    </el-alert>

    <el-empty v-if="items.length === 0" description="案例库中没有相似工况，可调整参数重试">
      <el-button type="primary" @click="router.push('/input')">调整参数</el-button>
    </el-empty>

    <el-card v-for="(it, i) in items" :key="it.case_id" style="margin-bottom: 12px">
      <template #header>
        <div class="card-head">
          <el-checkbox :model-value="store.compare.some(c => c.support_model === it.support_model)"
                       @change="store.toggleCompare(it)" />
          <el-button size="small" type="warning" plain
                     @click="store.toggleCompare(it); router.push('/modify')">去修改</el-button>
          <b>#{{ i + 1 }} {{ it.support_model }}</b>
          <el-tag v-if="i === 0" type="danger" style="margin-left: 8px">推荐</el-tag>
          <div class="sim">
            <el-progress :percentage="simPct(it.similarity)" :stroke-width="10"
                         :status="simType(it.similarity) || undefined" style="width: 180px" />
            <span>{{ simPct(it.similarity) }}%</span>
          </div>
        </div>
      </template>

      <p style="margin: 0 0 8px">案例：{{ it.working_face_name }}（{{ it.area_name }}）</p>

      <el-table :data="paramRows(it)" size="small" border style="margin-bottom: 8px">
        <el-table-column prop="k" label="关键参数" width="110" />
        <el-table-column prop="v" label="数值" />
      </el-table>

      <p style="margin: 4px 0; color: #909399"><b>主要差异：</b></p>
      <p v-for="d in it.diffs" :key="d" style="margin: 2px 0; color: #909399">· {{ d }}</p>
      <p style="margin: 4px 0 0; color: #67c23a">依据：{{ it.source }}</p>
    </el-card>
  </template>
</template>

<style scoped>
.card-head { display: flex; align-items: center; gap: 8px; }
.sim { margin-left: auto; display: flex; align-items: center; gap: 8px; }
</style>
