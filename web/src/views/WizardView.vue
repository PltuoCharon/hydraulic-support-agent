<template>
  <div class="wizard-page">
    <h2>选型向导</h2>
    <p class="note">四步完成选型：工况输入 → 参数确认 → 匹配结果 → 完成。引擎实际使用煤厚与倾角两个参数，本向导不收集不参与匹配的字段。</p>
    <el-steps :active="step" align-center class="steps">
      <el-step title="工况输入" />
      <el-step title="参数确认" />
      <el-step title="匹配结果" />
      <el-step title="完成" />
    </el-steps>

    <div v-if="step === 0" class="pane">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="140px" style="max-width: 480px; margin: 0 auto">
        <el-form-item label="煤层厚度(m)" prop="coal_thickness">
          <el-input-number v-model="form.coal_thickness" :step="0.1" :min="0.6" :max="24.9" />
        </el-form-item>
        <el-form-item label="煤层倾角(°)" prop="dip_angle">
          <el-input-number v-model="form.dip_angle" :step="0.5" :min="0" :max="45" />
        </el-form-item>
        <el-form-item label="返回候选数">
          <el-input-number v-model="form.top_n" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <div class="btns"><el-button type="primary" @click="toConfirm">下一步</el-button></div>
    </div>

    <div v-if="step === 1" class="pane">
      <el-descriptions :column="1" border style="max-width: 480px; margin: 0 auto">
        <el-descriptions-item label="煤层厚度">{{ form.coal_thickness }} m</el-descriptions-item>
        <el-descriptions-item label="煤层倾角">{{ form.dip_angle }}°</el-descriptions-item>
        <el-descriptions-item label="返回候选数">Top-{{ form.top_n }}</el-descriptions-item>
      </el-descriptions>
      <div class="btns">
        <el-button @click="step = 0">返回修改</el-button>
        <el-button type="primary" :loading="loading" @click="runMatch">确认并匹配</el-button>
      </div>
    </div>

    <div v-if="step === 2" class="pane">
      <div v-if="result" class="cards">
        <div v-for="(it, i) in result.items" :key="it.support_model" class="card">
          <b>#{{ i + 1 }} {{ it.support_model }}</b>
          <el-tooltip :content="it.support_source || '无来源记录'" placement="top">
            <el-tag size="small" :type="badge(it).type" class="tag">{{ badge(it).text }}</el-tag>
          </el-tooltip>
          <span class="sim">相似度 {{ (it.similarity * 100).toFixed(1) }}%</span>
        </div>
      </div>
      <el-empty v-else description="无结果" />
      <div class="btns">
        <el-button @click="step = 1">重新确认</el-button>
        <el-button @click="goFull">查看完整结果页</el-button>
        <el-button type="primary" @click="step = 3">下一步</el-button>
      </div>
    </div>

    <div v-if="step === 3" class="pane done">
      <p>选型流程完成。可继续：</p>
      <div class="btns">
        <el-button @click="restart">重新选型</el-button>
        <el-button @click="$router.push('/compare')">去对比分析</el-button>
        <el-button @click="$router.push('/chat')">去对话咨询</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { postMatch } from '../api'
import { useMatchStore } from '../store/match'
import { badge } from '../utils/badge'

const router = useRouter()
const store = useMatchStore()
const step = ref(0)
const loading = ref(false)
const formRef = ref(null)
const form = reactive({ coal_thickness: null, dip_angle: null, top_n: 5 })
const result = ref(null)

const rules = {
  coal_thickness: [
    { required: true, message: '必填', trigger: 'blur' },
    { type: 'number', min: 0.6, max: 24.9, message: '须大于 0.5 且小于 25（与后端口径一致）', trigger: 'blur' },
  ],
  dip_angle: [
    { required: true, message: '必填', trigger: 'blur' },
    { type: 'number', min: 0, max: 45, message: '0~45°', trigger: 'blur' },
  ],
}

const toConfirm = async () => {
  await formRef.value.validate()
  step.value = 1
}

const runMatch = async () => {
  loading.value = true
  try {
    const payload = { coal_thickness: form.coal_thickness, dip_angle: form.dip_angle, top_n: form.top_n }
    const data = await postMatch(payload)
    store.setResult({ coal_thickness: form.coal_thickness, dip_angle: form.dip_angle }, data)
    result.value = data
    step.value = 2
  } catch (e) {
    const d = e.response?.data?.detail
    const msg = Array.isArray(d) ? d.map(x => `${x.loc?.slice(-1)}: ${x.msg}`).join('；') : (d || e.message)
    ElMessage.error('匹配失败：' + msg)
  } finally {
    loading.value = false
  }
}

const goFull = () => { router.push('/result') }
const restart = () => { result.value = null; form.coal_thickness = null; form.dip_angle = null; step.value = 0 }
</script>

<style scoped>
.wizard-page { padding: 16px; }
.steps { margin: 20px auto; max-width: 720px; }
.pane { max-width: 720px; margin: 24px auto; }
.btns { text-align: center; margin-top: 20px; }
.cards .card { padding: 10px 14px; border: 1px solid #ebeef5; border-radius: 6px; margin-bottom: 8px; display: flex; gap: 10px; align-items: center; }
.tag { margin-left: 4px; }
.sim { color: #666; margin-left: auto; }
.note { color: #666; font-size: 13px; }
.done p { text-align: center; }
</style>
