<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useMatchStore } from '../store/match'
import { getRequirement, postRecalc } from '../api'

const router = useRouter()
const store = useMatchStore()

const target = computed(() => store.compare[0] || store.result?.items?.[0] || null)

const form = reactive({ bore: 360, column_count: 4, pump_pressure: 31.5 })
const result = ref(null)      // recalc 返回
const baseline = ref(null)    // 首次结果作基线，用于"已变化"判断
const submitting = ref(false)

onMounted(async () => {
  if (!store.required && store.conditions?.coal_thickness) {
    try {
      const req = await getRequirement(store.conditions.coal_thickness)
      store.setRequired(req || null)
    } catch (e) { /* 静默 */ }
  }
  runRecalc()   // 进页先算一次基线
})

const isChanged = (k) => {
  if (!baseline.value || !result.value) return false
  return Math.abs(baseline.value.new_params[k] - result.value.new_params[k]) > 0.05
}
const alarmList = computed(() => result.value?.alarms || [])
const alarmParam = (k) => alarmList.value.find(a => a.param === k)

const rules = {
  bore: [{ required: true, type: 'number', min: 100, max: 500, message: '缸径 100~500 mm', trigger: 'blur' }],
  column_count: [{ required: true, type: 'number', min: 2, max: 6, message: '立柱数 2~6 根', trigger: 'blur' }],
  pump_pressure: [{ required: true, type: 'number', min: 10, max: 40, message: '泵站压力 10~40 MPa', trigger: 'blur' }],
}

const runRecalc = async () => {
  submitting.value = true
  try {
    const data = await postRecalc({
      support_model: target.value?.support_model,
      bore: form.bore, column_count: form.column_count,
      pump_pressure: form.pump_pressure,
      coal_thickness: store.conditions?.coal_thickness ?? 8.0,
    })
    if (!baseline.value) baseline.value = JSON.parse(JSON.stringify(data))
    result.value = data
    if (data.alarms?.length) {
      ElMessage.error(`不满足工况需求：${data.alarms.map(a => a.param).join('、')}`)
    } else {
      ElMessage.success('参数达标，满足工况需求')
    }
  } catch (e) {
    ElMessage.error('重算失败：' + (e.response?.data?.detail || e.message))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <h2>部件修改</h2>

  <el-empty v-if="!target" description="先完成匹配，在结果页点「去修改」进入">
    <el-button type="primary" @click="router.push('/input')">去输入工况</el-button>
  </el-empty>

  <template v-else>
    <el-descriptions :column="2" border style="margin-bottom: 16px">
      <el-descriptions-item label="支架型号">{{ target.support_model }}</el-descriptions-item>
      <el-descriptions-item label="工况采高">{{ store.conditions?.coal_thickness }} m</el-descriptions-item>
    </el-descriptions>

    <el-alert v-if="store.required" type="info" :closable="false" style="margin-bottom: 12px"
              :title="`工况需求：支护强度 ≥ ${store.required.intensity} MPa，工作阻力 ≥ ${store.required.resistance} kN`" />

    <el-alert v-if="alarmList.length" type="error" :closable="false" style="margin-bottom: 12px"
              :title="`${alarmList.length} 项不满足工况需求！`">
      <p v-for="a in alarmList" :key="a.param" style="margin: 2px 0">
        {{ a.param }}：当前 {{ a.value }} &lt; 需求 {{ a.required }}
      </p>
      <el-button size="small" type="danger" style="margin-top: 6px"
                 @click="form.bore += 40; runRecalc()">建议：缸径 +40mm 重算</el-button>
    </el-alert>

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
          <el-button type="primary" :loading="submitting" @click="runRecalc">提交重算</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header><b>参数链（链式变化：初撑力 → 工作阻力 → 支护强度）</b></template>
      <template v-if="result">
        <p :style="isChanged('setting_load') ? 'background:#fdf6ec; padding:4px 8px' : ''">
          初撑力：{{ result.new_params.setting_load }} kN
          <el-tag v-if="isChanged('setting_load')" size="small" type="warning" style="margin-left: 8px">已变化</el-tag>
        </p>
        <p :style="isChanged('working_resistance') ? 'background:#fdf6ec; padding:4px 8px' : ''">
          工作阻力：{{ result.new_params.working_resistance }} kN
          <el-tag v-if="isChanged('working_resistance')" size="small" type="warning" style="margin-left: 8px">已变化</el-tag>
          <el-tag v-if="alarmParam('工作阻力')" size="small" type="danger" style="margin-left: 8px">低于需求!</el-tag>
        </p>
        <p :style="isChanged('intensity') ? 'background:#fdf6ec; padding:4px 8px' : ''">
          支护强度：<span :style="alarmParam('支护强度') ? 'color:#f56c6c; font-weight:bold' : ''">
            {{ result.new_params.intensity }}</span> MPa
          <el-tag v-if="isChanged('intensity')" size="small" type="warning" style="margin-left: 8px">已变化</el-tag>
          <el-tag v-if="alarmParam('支护强度')" size="small" type="danger" style="margin-left: 8px">低于需求!</el-tag>
        </p>
        <p style="color:#909399; margin: 8px 0 0">公式：初撑力=n·P泵·π/4·D² → 工作阻力=初撑力/初撑比 → 支护强度=F·η/控顶面积</p>
      </template>
      <p v-else style="color:#909399; margin: 0">提交后显示</p>
    </el-card>
  </template>
</template>
