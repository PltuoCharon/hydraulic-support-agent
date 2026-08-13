<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useMatchStore } from '../store/match'

const router = useRouter()
const store = useMatchStore()

// 修改对象 = 结果页勾选的第一个支架；没勾选就取推荐第一
const target = computed(() => store.compare[0] || store.result?.items?.[0] || null)

const form = reactive({ bore: 360, column_count: 4, pump_pressure: 31.5 })
const submitting = ref(false)

const rules = {
  bore: [{ required: true, type: 'number', min: 100, max: 500, message: '缸径 100~500 mm', trigger: 'blur' }],
  column_count: [{ required: true, type: 'number', min: 2, max: 6, message: '立柱数 2~6 根', trigger: 'blur' }],
  pump_pressure: [{ required: true, type: 'number', min: 10, max: 40, message: '泵站压力 10~40 MPa', trigger: 'blur' }],
}

// D6 接入 /api/recalc；当前占位
const onRecalc = () => {
  submitting.value = true
  setTimeout(() => {
    submitting.value = false
    ElMessage.info('参数链重算将在下一步接入，当前为 D5 展示版')
  }, 400)
}

const readOnlyRows = computed(() => target.value ? [
  { k: '工作阻力', v: target.value.working_resistance != null ? target.value.working_resistance + ' kN' : '—' },
  { k: '支护强度', v: target.value.intensity != null ? target.value.intensity + ' MPa' : '—' },
  { k: '支架高度', v: target.value.height_min != null && target.value.height_max != null
                    ? `${target.value.height_min}~${target.value.height_max} m` : '—' },
  { k: '支架重量', v: target.value.weight != null ? target.value.weight + ' t' : '—' },
  { k: '中心距',   v: target.value.center_dist != null ? target.value.center_dist + ' m' : '—' },
  { k: '初撑力',   v: target.value.initial_force != null ? target.value.initial_force + ' kN' : '—' },
] : [])
</script>

<template>
  <h2>部件修改</h2>

  <el-empty v-if="!target" description="先完成匹配，在结果页点「去修改」进入">
    <el-button type="primary" @click="router.push('/input')">去输入工况</el-button>
  </el-empty>

  <template v-else>
    <el-descriptions :column="2" border style="margin-bottom: 16px">
      <el-descriptions-item label="支架型号">{{ target.support_model }}</el-descriptions-item>
      <el-descriptions-item label="案例">{{ target.area_name }}·{{ target.working_face_name }}</el-descriptions-item>
    </el-descriptions>

    <el-alert v-if="store.required" type="info" :closable="false" style="margin-bottom: 16px"
              :title="`工况需求：支护强度 ≥ ${store.required.intensity} MPa，工作阻力 ≥ ${store.required.resistance} kN`" />
    <el-alert v-else type="warning" :closable="false" style="margin-bottom: 16px"
              title="工况需求值未获取到（需先完成一次匹配）" />

    <el-card style="margin-bottom: 16px">
      <template #header><b>可修改参数（立柱 + 泵站）</b></template>
      <el-form :model="form" :rules="rules" label-width="130px" style="max-width: 420px">
        <el-form-item label="立柱缸径" prop="bore">
          <el-input-number v-model="form.bore" :min="100" :max="500" :step="20" />
          <span style="margin-left: 8px; color: #909399">mm</span>
        </el-form-item>
        <el-form-item label="立柱数量" prop="column_count">
          <el-input-number v-model="form.column_count" :min="2" :max="6" :step="1" />
          <span style="margin-left: 8px; color: #909399">根</span>
        </el-form-item>
        <el-form-item label="泵站压力" prop="pump_pressure">
          <el-input-number v-model="form.pump_pressure" :min="10" :max="40" :step="0.5" />
          <span style="margin-left: 8px; color: #909399">MPa</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="onRecalc">提交重算</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header><b>只读参数（由推荐结果带入）</b></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item v-for="r in readOnlyRows" :key="r.k" :label="r.k">{{ r.v }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </template>
</template>
