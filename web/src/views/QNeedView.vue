<template>
  <div class="qneed-view">
    <div class="section-head">
      <div>
        <span>Support Requirement</span>
        <h2>支护需求计算</h2>
        <p>
          根据采高、顶板来压步距、控顶宽度和直接顶充填系数，
          计算三种方法下的需求支护强度，并采用控制值。
        </p>
      </div>
    </div>

    <FormulaCard
      formula-id="F-QN-001~004"
      title="需求支护强度控制关系"
      formula="q_need = max(p1, p2, p3)"
      description="p1、p2、p3 分别对应三条已登记计算链；程序取三式中的最大值作为需求支护强度。"
      source="纵帅等《大采高综采工作面液压支架选型研究及应用》及当前 Formula Registry"
    />

    <div class="work-grid">
      <section class="engineering-card">
        <div class="card-title">
          <div>
            <strong>计算输入</strong>
            <span>Engineering Inputs</span>
          </div>

          <button
            class="example-button"
            @click="fillXieqiao"
          >
            填入谢桥复核实例
          </button>
        </div>

        <el-form
          :model="form"
          label-width="190px"
        >
          <el-form-item label="采高 hm">
            <el-input-number
              v-model="form.hm"
              :min="0.5"
              :max="10"
              :step="0.1"
              controls-position="right"
            />
            <span class="unit">m</span>
          </el-form-item>

          <el-form-item label="老顶初次来压步距 L1">
            <el-input-number
              v-model="form.l1"
              :min="5"
              :max="100"
              :step="1"
              controls-position="right"
            />
            <span class="unit">m</span>
          </el-form-item>

          <el-form-item label="基本顶周期来压步距 Lp">
            <el-input-number
              v-model="form.lp"
              :min="3"
              :max="60"
              :step="0.1"
              controls-position="right"
            />
            <span class="unit">m</span>
          </el-form-item>

          <el-form-item label="控顶宽度 Bc">
            <el-input-number
              v-model="form.bc"
              :min="1"
              :max="15"
              :step="0.05"
              controls-position="right"
            />
            <span class="unit">m</span>
          </el-form-item>

          <el-form-item label="直接顶充填系数 N">
            <el-input-number
              v-model="form.n"
              :min="0.2"
              :max="5"
              :step="0.01"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>

          <div class="parameter-note">
            N = 直接顶厚度 / 采高。
            本页参数语义按当前专业术语字典执行。
          </div>

          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              @click="run"
            >
              开始计算
            </el-button>

            <el-button
              @click="clearResult"
            >
              清空结果
            </el-button>
          </el-form-item>
        </el-form>
      </section>

      <section class="result-stage">
        <template v-if="res">
          <div class="result-heading">
            <div>
              <span>Calculation Result</span>
              <h3>需求支护强度</h3>
            </div>

            <strong>
              {{ res.q_need_mpa }}
              <small>MPa</small>
            </strong>
          </div>

          <div class="method-grid">
            <div class="method-card">
              <span>p1</span>
              <strong>{{ res.p1_mpa }} MPa</strong>
              <small>岩重法</small>
            </div>

            <div class="method-card">
              <span>p2</span>
              <strong>{{ res.p2_mpa }} MPa</strong>
              <small>老顶来压步距法</small>
            </div>

            <div class="method-card">
              <span>p3</span>
              <strong>{{ res.p3_mpa }} MPa</strong>
              <small>统计公式</small>
            </div>
          </div>

          <div class="result-detail">
            <div>
              <span>控制式</span>
              <strong>{{ res.governing }}</strong>
            </div>

            <div>
              <span>取值规则</span>
              <strong>{{ res.rule }}</strong>
            </div>
          </div>

          <div class="source-block">
            <span>计算来源</span>
            <p>{{ res.source }}</p>
          </div>
        </template>

        <EmptyState
          v-else
          title="等待计算"
          description="填写左侧参数后执行计算。结果区将展示 p1、p2、p3 以及最终控制值 q_need。"
        />
      </section>
    </div>

    <el-alert
      type="warning"
      :closable="false"
      show-icon
      title="q_need 的单位为 MPa，表示需求支护强度，不等同于整架工作阻力 kN。两者之间不能在未核实支护面积定义的情况下直接换算。"
    />
  </div>
</template>

<script setup>
import {
  reactive,
  ref,
} from 'vue'

import { postQNeed } from '../api'

import FormulaCard from '../components/ui/FormulaCard.vue'
import EmptyState from '../components/ui/EmptyState.vue'


const form = reactive({
  hm: 6.0,
  l1: 25,
  lp: 15,
  bc: 5,
  n: 1.33,
})

const res = ref(null)
const loading = ref(false)


const run = async () => {
  loading.value = true

  try {
    res.value = await postQNeed({
      ...form,
    })
  } catch {
    // Axios 拦截器统一提示。
  } finally {
    loading.value = false
  }
}


const fillXieqiao = async () => {
  Object.assign(
    form,
    {
      hm: 6.0,
      l1: 25,
      lp: 15,
      bc: 5,
      n: 1.33,
    },
  )

  await run()
}


const clearResult = () => {
  res.value = null
}
</script>

<style scoped>
.qneed-view {
  display: grid;
  gap: 16px;
}

.section-head span,
.result-heading span {
  color: #2f80ed;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.section-head h2 {
  margin: 4px 0 5px;
  color: #17324d;
  font-size: 21px;
}

.section-head p {
  max-width: 820px;
  margin: 0;
  color: #667085;
  font-size: 13px;
  line-height: 1.65;
}

.work-grid {
  display: grid;
  grid-template-columns:
    minmax(420px, .86fr)
    minmax(0, 1.14fr);
  gap: 16px;
}

.engineering-card,
.result-stage {
  padding: 19px;
  background: #fff;
  border: 1px solid #dfe5eb;
  border-radius: 9px;
}

.card-title,
.result-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 20px;
}

.card-title > div {
  display: grid;
  gap: 3px;
}

.card-title strong {
  color: #17324d;
  font-size: 15px;
}

.card-title span {
  color: #8a94a3;
  font-size: 10px;
  text-transform: uppercase;
}

.example-button {
  padding: 5px 8px;
  color: #2f80ed;
  background: transparent;
  border: 0;
  cursor: pointer;
  font-size: 12px;
}

.unit {
  margin-left: 8px;
  color: #667085;
}

.parameter-note {
  margin:
    -4px 0 18px 190px;
  color: #8a94a3;
  font-size: 12px;
}

.result-heading h3 {
  margin: 4px 0 0;
  color: #17324d;
  font-size: 17px;
}

.result-heading > strong {
  color: #123b61;
  font-size: 34px;
}

.result-heading small {
  margin-left: 4px;
  color: #667085;
  font-size: 13px;
  font-weight: 500;
}

.method-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.method-card {
  display: grid;
  gap: 6px;
  padding: 14px;
  background: #f7f9fb;
  border: 1px solid #e6ebf0;
  border-radius: 7px;
}

.method-card span {
  color: #8a94a3;
  font-family: Consolas, monospace;
  font-size: 11px;
}

.method-card strong {
  color: #17324d;
  font-size: 17px;
}

.method-card small {
  color: #667085;
}

.result-detail {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.result-detail > div {
  display: grid;
  gap: 5px;
  padding: 12px 14px;
  border-bottom: 1px solid #e6ebf0;
}

.result-detail span,
.source-block span {
  color: #8a94a3;
  font-size: 11px;
}

.result-detail strong {
  color: #344054;
  font-size: 13px;
}

.source-block {
  margin-top: 15px;
  padding-top: 12px;
  border-top: 1px solid #e6ebf0;
}

.source-block p {
  margin: 5px 0 0;
  color: #667085;
  font-size: 12px;
  line-height: 1.6;
}

:deep(.el-input-number) {
  width: 220px;
}

@media (max-width: 1150px) {
  .work-grid {
    grid-template-columns: 1fr;
  }
}
</style>
