<template>
  <div class="jack-view">
    <div class="page-head">
      <div>
        <h2>推移千斤顶参数设计</h2>
        <p>
          根据显式推力需求和工作压力反算候选缸径，
          并在给定活塞杆直径时校核杆腔拉力。
        </p>
      </div>
    </div>

    <el-alert
      title="计算边界"
      type="info"
      :closable="false"
      show-icon
      class="boundary-alert"
    >
      <template #default>
        当前模块为参数化设计辅助。
        不自动生成活塞杆直径、行程、工作压力或效率参数，
        也不自动判断推输送机与移架对应的油腔方向。
      </template>
    </el-alert>

    <el-row :gutter="18">
      <el-col :xs="24" :lg="10">
        <el-card shadow="never">
          <template #header>
            <b>设计输入</b>
          </template>

          <el-form
            :model="form"
            label-width="155px"
          >
            <el-form-item label="无杆腔推力需求">
              <el-input-number
                v-model="form.push_required_kn"
                :min="0"
                :step="10"
                controls-position="right"
                placeholder="请输入"
              />
              <span class="unit">kN</span>
            </el-form-item>

            <el-form-item label="工作压力">
              <el-input-number
                v-model="form.pressure_mpa"
                :min="0"
                :step="0.5"
                controls-position="right"
                placeholder="请输入"
              />
              <span class="unit">MPa</span>
            </el-form-item>

            <el-divider content-position="left">
              可选参数
            </el-divider>
            <el-form-item label="活塞杆直径">
              <el-input-number
                v-model="form.rod_mm"
                :min="0"
                :step="5"
                controls-position="right"
                placeholder="可选"
              />
              <span class="unit">mm</span>
            </el-form-item>

            <el-form-item label="杆腔拉力需求">
              <el-input-number
                v-model="form.pull_required_kn"
                :min="0"
                :step="10"
                controls-position="right"
                placeholder="可选"
              />
              <span class="unit">kN</span>
            </el-form-item>

            <el-alert
              v-if="pullNeedsRod"
              type="warning"
              :closable="false"
              show-icon
              title="填写杆腔拉力需求时必须同时提供活塞杆直径。"
              class="inline-alert"
            />

            <el-form-item label="行程">
              <el-input-number
                v-model="form.stroke_mm"
                :min="0"
                :step="50"
                controls-position="right"
                placeholder="可选"
              />
              <span class="unit">mm</span>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                :disabled="!ready"
                @click="runDesign"
              >
                开始计算
              </el-button>

              <el-button @click="clearResult">
                清空结果
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="14">
        <el-card
          v-if="result"
          shadow="never"
        >
          <template #header>
            <b>计算结果</b>
          </template>

          <el-descriptions
            :column="2"
            border
          >
            <el-descriptions-item label="理论缸径">
              <b>{{ result.bore_calc_mm }}</b> mm
            </el-descriptions-item>

            <el-descriptions-item label="候选缸径">
              <b>{{ result.bore_candidate_mm }}</b> mm
            </el-descriptions-item>

            <el-descriptions-item label="实际无杆腔推力">
              <b>{{ result.push_actual_kn }}</b> kN
            </el-descriptions-item>

            <el-descriptions-item label="推力需求校核">
              <el-tag :type="result.push_ok ? success : danger">
                {{ result.push_ok ? 满足 : 不满足 }}
              </el-tag>
            </el-descriptions-item>

            <template v-if="result.rod_mm !== undefined">
              <el-descriptions-item label="活塞杆直径">
                {{ result.rod_mm }} mm
              </el-descriptions-item>

              <el-descriptions-item label="实际杆腔拉力">
                <b>{{ result.pull_actual_kn }}</b> kN
              </el-descriptions-item>
            </template>

            <template v-if="result.pull_required_kn !== undefined">
              <el-descriptions-item label="杆腔拉力需求">
                {{ result.pull_required_kn }} kN
              </el-descriptions-item>

              <el-descriptions-item label="拉力需求校核">
                <el-tag :type="result.pull_ok ? success : danger">
                  {{ result.pull_ok ? 满足 : 不满足 }}
                </el-tag>
              </el-descriptions-item>
            </template>

            <el-descriptions-item
              v-if="result.stroke_mm !== undefined"
              label="行程"
            >
              {{ result.stroke_mm }} mm
              <el-tag size="small" type="info">
                用户输入
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          <el-alert
            v-if="result.mt_t94_verified === false"
            title="MT/T94 尺寸系列尚未核验"
            type="warning"
            :closable="false"
            show-icon
            class="standard-alert"
          >
            <template #default>
              当前候选缸径仅按项目已录入的 GB/T 2348
              常用缸径列表圆整，尚未完成 MT/T94
              千斤顶缸径和活塞杆径系列核验。
            </template>
          </el-alert>
        </el-card>

        <el-card
          v-else
          shadow="never"
          class="empty-card"
        >
          <el-empty
            description="输入无杆腔推力需求和工作压力后执行计算。"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import {
  computed,
  ref,
} from 'vue'

import {
  postPushJackDesign,
} from '../api'


const form = ref({
  push_required_kn: null,
  pressure_mpa: null,
  rod_mm: null,
  pull_required_kn: null,
  stroke_mm: null,
})

const loading = ref(false)
const result = ref(null)


const pullNeedsRod = computed(() =>
  form.value.pull_required_kn != null
  && form.value.rod_mm == null
)


const ready = computed(() =>
  form.value.push_required_kn != null
  && form.value.push_required_kn > 0
  && form.value.pressure_mpa != null
  && form.value.pressure_mpa > 0
  && !pullNeedsRod.value
)


const runDesign = async () => {
  if (!ready.value) {
    return
  }

  const payload = {
    push_required_kn: form.value.push_required_kn,
    pressure_mpa: form.value.pressure_mpa,
  }

  if (form.value.rod_mm != null) {
    payload.rod_mm = form.value.rod_mm
  }

  if (form.value.pull_required_kn != null) {
    payload.pull_required_kn = form.value.pull_required_kn
  }

  if (form.value.stroke_mm != null) {
    payload.stroke_mm = form.value.stroke_mm
  }

  loading.value = true

  try {
    result.value = await postPushJackDesign(payload)
  } finally {
    loading.value = false
  }
}


const clearResult = () => {
  result.value = null
}
</script>


<style scoped>
.jack-view {
  display: grid;
  gap: 18px;
}

.page-head h2 {
  margin: 0;
  color: #17324d;
  font-size: 20px;
}

.page-head p {
  margin: 7px 0 0;
  color: #667085;
  font-size: 13px;
  line-height: 1.65;
}

.boundary-alert {
  margin-bottom: 2px;
}

.inline-alert {
  margin: -4px 0 18px;
}

.standard-alert {
  margin-top: 18px;
}

.unit {
  margin-left: 9px;
  color: #667085;
  font-size: 12px;
}

.empty-card {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.el-input-number) {
  width: 210px;
}
</style>
