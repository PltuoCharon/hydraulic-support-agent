<script setup>
import { ref, reactive } from 'vue'

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

// D3: 提交到 /api/match（当前版本由 厚度+倾角 驱动，其余字段为工况档案）
const submit = async () => {
  await formRef.value.validate()
  console.log('submit', form)
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
      <el-button type="primary" :loading="loading" @click="submit">开始匹配</el-button>
      <el-button @click="reset">重置</el-button>
    </el-form-item>
  </el-form>
</template>
