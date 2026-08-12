<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { postMatch } from '../api'
import { useMatchStore } from '../store/match'

const router = useRouter()
const store = useMatchStore()

// 矿区路径回填: store 里有预填条件则灌进表单(可再修改)
onMounted(() => {
  if (store.conditions) {
    Object.assign(form, store.conditions)
    if (store.fromArea) {
      ElMessage.success(`已带入【${store.fromArea.area_name}】工况参数，可修改后匹配`)
    }
  }
})

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  coal_thickness: null,     // 煤层厚度(m) —— 匹配核心输入
  dip_angle: null,          // 煤层倾角(°) —— 匹配核心输入
  mining_height_min: null,  // 采高下限(m)
  mining_height_max: null,  // 采高上限(m)
  hardness_f: null,         // 煤硬度系数 f
  roof_category: '',        // 顶板类别
  floor_pressure: null,     // 底板比压(MPa)
  mine_pressure: '',        // 矿压显现等级
  gas_level: '',            // 瓦斯等级
  depth: null,              // 埋深(m)
  face_length: null,        // 工作面长度(m)
})

const rules = {
  coal_thickness: [
    { required: true, message: '必填', trigger: 'blur' },
    { type: 'number', min: 0.5, max: 25, message: '0.5~25m', trigger: 'blur' },
  ],
  dip_angle: [
    { required: true, message: '必填', trigger: 'blur' },
    { type: 'number', min: 0, max: 45, message: '0~45°', trigger: 'blur' },
  ],
  hardness_f: [
    { type: 'number', min: 0.1, max: 6, message: '0.1~6', trigger: 'blur' },
  ],
  roof_category: [{ required: true, message: '必选', trigger: 'change' }],
  mine_pressure: [{ required: true, message: '必选', trigger: 'change' }],
  gas_level: [{ required: true, message: '必选', trigger: 'change' }],
  depth: [
    { type: 'number', min: 0, max: 1500, message: '0~1500m', trigger: 'blur' },
  ],
  face_length: [
    { type: 'number', min: 20, max: 500, message: '20~500m', trigger: 'blur' },
  ],
}

const submit = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    const payload = {
      coal_thickness: form.coal_thickness,
      dip_angle: form.dip_angle,
      top_n: 5,
    }
    const data = await postMatch(payload)
    store.setResult({ ...form }, data)
    router.push('/result')
  } catch (e) {
    ElMessage.error('匹配失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}
const reset = () => formRef.value.resetFields()
</script>

<template>
  <h2>工况参数输入</h2>
  <el-form ref="formRef" :model="form" :rules="rules"
           label-width="130px" style="max-width: 520px">
    <el-divider content-position="left">匹配核心参数</el-divider>
    <el-form-item label="煤层厚度(m)" prop="coal_thickness">
      <el-input-number v-model="form.coal_thickness" :step="0.1" :min="0.5" :max="25" />
    </el-form-item>
    <el-form-item label="煤层倾角(°)" prop="dip_angle">
      <el-input-number v-model="form.dip_angle" :step="0.5" :min="0" :max="45" />
    </el-form-item>
    <el-divider content-position="left">工况档案（后续版本参与筛选）</el-divider>
    <el-form-item label="采高下限(m)" prop="mining_height_min">
      <el-input-number v-model="form.mining_height_min" :step="0.1" :min="0.5" :max="10" />
    </el-form-item>
    <el-form-item label="采高上限(m)" prop="mining_height_max">
      <el-input-number v-model="form.mining_height_max" :step="0.1" :min="0.5" :max="10" />
    </el-form-item>
    <el-form-item label="煤硬度 f" prop="hardness_f">
      <el-input-number v-model="form.hardness_f" :step="0.1" :min="0.1" :max="6" />
    </el-form-item>
    <el-form-item label="顶板类别" prop="roof_category">
      <el-select v-model="form.roof_category" placeholder="请选择">
        <el-option v-for="o in ['不稳定','中等稳定','稳定','坚硬']" :key="o" :label="o" :value="o" />
      </el-select>
    </el-form-item>
    <el-form-item label="底板比压(MPa)" prop="floor_pressure">
      <el-input-number v-model="form.floor_pressure" :step="0.1" :min="0" :max="50" />
    </el-form-item>
    <el-form-item label="矿压显现" prop="mine_pressure">
      <el-select v-model="form.mine_pressure" placeholder="请选择">
        <el-option v-for="o in ['来压不明显','来压明显','来压强烈','来压极强烈']" :key="o" :label="o" :value="o" />
      </el-select>
    </el-form-item>
    <el-form-item label="瓦斯等级" prop="gas_level">
      <el-select v-model="form.gas_level" placeholder="请选择">
        <el-option v-for="o in ['低瓦斯','高瓦斯','突出']" :key="o" :label="o" :value="o" />
      </el-select>
    </el-form-item>
    <el-form-item label="埋深(m)" prop="depth">
      <el-input-number v-model="form.depth" :step="10" :min="0" :max="1500" />
    </el-form-item>
    <el-form-item label="面长(m)" prop="face_length">
      <el-input-number v-model="form.face_length" :step="5" :min="20" :max="500" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" :loading="loading" :disabled="loading" @click="submit">开始匹配</el-button>
      <el-button @click="reset">重置</el-button>
    </el-form-item>
  </el-form>
</template>
