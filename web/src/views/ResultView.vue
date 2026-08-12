<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMatchStore } from '../store/match'

const router = useRouter()
const store = useMatchStore()

const items = computed(() => store.result?.items || [])
const cond = computed(() => store.conditions)

const simPct = (s) => (s * 100).toFixed(1) + '%'
const simType = (s) => s >= 0.7 ? 'success' : s >= 0.5 ? 'warning' : 'info'
</script>

<template>
  <h2>推荐结果</h2>

  <el-empty v-if="!store.result" description="还没有匹配结果">
    <el-button type="primary" @click="router.push('/input')">去输入工况</el-button>
  </el-empty>

  <template v-else>
    <el-descriptions :column="3" border style="margin-bottom: 16px">
      <el-descriptions-item label="煤层厚度">{{ cond.coal_thickness }} m</el-descriptions-item>
      <el-descriptions-item label="煤层倾角">{{ cond.dip_angle }}°</el-descriptions-item>
      <el-descriptions-item label="候选数">{{ store.result.total }}</el-descriptions-item>
    </el-descriptions>

    <el-card v-for="(it, i) in items" :key="it.case_id" style="margin-bottom: 12px">
      <template #header>
        <b>#{{ i + 1 }} {{ it.support_model }}</b>
        <el-tag :type="simType(it.similarity)" style="margin-left: 12px">
          相似度 {{ simPct(it.similarity) }}
        </el-tag>
        <el-tag v-if="i === 0" type="danger" style="margin-left: 8px">推荐</el-tag>
      </template>
      <p>案例：{{ it.working_face_name }}（{{ it.area_name }}）｜
         阻力 {{ it.working_resistance }} kN｜支护强度 {{ it.intensity ?? '未查到公开参数' }} MPa</p>
      <p v-for="d in it.diffs" :key="d" style="color: #909399; margin: 2px 0">{{ d }}</p>
      <p style="color: #67c23a">依据：{{ it.source }}</p>
    </el-card>
  </template>
</template>
