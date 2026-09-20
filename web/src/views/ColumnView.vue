<template>
  <div class="column-view">

    <div class="page-head">
      <div>
        <h2>立柱设计与强度校核</h2>
        <p>
          根据支架工作阻力反算立柱缸径，并对缸筒壁厚、
          材料应力及压杆稳定性进行参数化校核。
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
        本模块用于公式复现、参数设计辅助和方案比较。
        材料性能、安全系数、载荷与边界条件应结合实际设计资料复核；
        当前结果不直接作为产品制造依据。
      </template>
    </el-alert>

    <el-card
      v-if="designContext"
      shadow="never"
      class="design-context"
      style="margin-bottom: 18px"
    >
      <template #header>
        <b>设计上下文</b>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="来源">
          {{
            designContext.source_type === "selected_support"
              ? "推荐支架"
              : "需求计算"
          }}
        </el-descriptions-item>

        <el-descriptions-item label="支架型号">
          {{ designContext.target.support_model || "—" }}
        </el-descriptions-item>

        <el-descriptions-item label="目标工作阻力">
          {{ designContext.target.resistance_kn }} kN
        </el-descriptions-item>

        <el-descriptions-item label="数据状态">
          {{ designContext.provenance?.data_status || "未提供" }}
        </el-descriptions-item>

        <el-descriptions-item label="来源记录" :span="2">
          {{ designContext.provenance?.source_text || "未提供" }}
        </el-descriptions-item>
      </el-descriptions>

      <el-alert
        v-if="contextConfirmed === false"
        type="warning"
        :closable="false"
        show-icon
        title="请确认该工作阻力作为本次立柱设计载荷依据。"
        style="margin-top: 12px"
      />

      <el-button
        v-if="contextConfirmed === false"
        type="primary"
        style="margin-top: 12px"
        @click="confirmDesignContext"
      >
        确认并用于立柱设计
      </el-button>

      <el-tag
        v-else
        type="success"
        style="margin-top: 12px"
      >
        设计上下文已确认
      </el-tag>
    </el-card>

    <FormulaCard
      formula-id="F-COL-001~003"
      title="立柱承载与缸径设计关系"
      formula="P = n × (π/4) × D² × p × η"
      description="由设计工作阻力、承载立柱根数、立柱工作压力和显式输入的历史修正系数 η（物理口径待核）反算理论缸径，并向上圆整到程序维护的标准缸径系列。"
      source="标准缸径系列：GB/T 2348；含 η 的计算关系为项目参数化计算式，η 物理口径待核。"
      class="column-formula"
    />

    <el-tabs v-model="tab" class="main-tabs">

      <!-- ==================================================
           A. 缸径设计
           ================================================== -->
      <el-tab-pane label="缸径设计" name="design">

        <el-row :gutter="18">

          <el-col :xs="24" :lg="10">
            <el-card shadow="never">
              <template #header>
                <b>设计输入</b>
              </template>

              <el-form
                :model="designForm"
                label-width="150px"
              >

                <el-form-item label="设计工作阻力">
                  <el-input-number
                    v-model="designForm.p_kn"
                    :min="100"
                    :max="50000"
                    :step="100"
                    controls-position="right"
                  />
                  <span class="unit">kN</span>
                </el-form-item>

                <el-form-item label="承载立柱根数">
                  <el-input-number
                    v-model="designForm.n"
                    :min="1"
                    :max="8"
                    :step="1"
                    :precision="0"
                    controls-position="right"
                  />
                  <span class="unit">根</span>
                </el-form-item>

                <el-form-item label="立柱工作压力">
                  <el-input-number
                    v-model="designForm.p_mpa"
                    :min="5"
                    :max="50"
                    :step="0.5"
                    controls-position="right"
                  />
                  <span class="unit">MPa</span>
                </el-form-item>

                <el-form-item label="历史修正系数 η（待核）">
                  <el-input-number
                    v-model="designForm.eta"
                    :min="0.8"
                    :max="1.0"
                    :step="0.01"
                    :precision="2"
                    controls-position="right"
                  />
                </el-form-item>

                <el-divider content-position="left">
                  初撑力校核（可选）
                </el-divider>

                <el-form-item label="启用初撑力校核">
                  <el-switch v-model="enableSetting" />
                </el-form-item>

                <el-form-item
                  v-if="enableSetting"
                  label="初撑力"
                >
                  <el-input-number
                    v-model="designForm.p_set_kn"
                    :min="0"
                    :max="50000"
                    :step="100"
                    controls-position="right"
                  />
                  <span class="unit">kN</span>
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    :loading="designLoading"
                    :disabled="designReady === false"
                    @click="runDesign"
                  >
                    开始计算
                  </el-button>

                  <el-button @click="fillDesignExample">
                    填入计算示例
                  </el-button>

                  <el-button @click="clearDesign">
                    清空结果
                  </el-button>
                </el-form-item>

              </el-form>
            </el-card>
          </el-col>

          <el-col :xs="24" :lg="14">

            <el-card
              v-if="designRes"
              shadow="never"
            >
              <template #header>
                <b>计算结果</b>
              </template>

              <el-descriptions
                :column="2"
                border
              >
                <el-descriptions-item
                  v-if="designRes.record_id != null"
                  label="计算记录"
                >
                  <el-tag
                    type="info"
                    style="cursor: pointer"
                    @click="openRecordDetail(designRes.record_id)"
                  >
                    #{{ designRes.record_id }}
                  </el-tag>
                </el-descriptions-item>

                <el-descriptions-item label="理论缸径">
                  <b>{{ designRes.d_calc_mm }}</b> mm
                </el-descriptions-item>

                <el-descriptions-item label="标准缸径">
                  <b>{{ designRes.d_std_mm }}</b> mm
                </el-descriptions-item>

                <el-descriptions-item label="圆整后计算承载力">
                  <b>{{ designRes.p_actual_kn }}</b> kN
                </el-descriptions-item>

                <el-descriptions-item label="圆整方向">
                  <el-tag type="success">
                    向上圆整
                  </el-tag>
                </el-descriptions-item>

                <template v-if="designRes.setting_ratio_pct !== undefined">
                  <el-descriptions-item label="初撑力比">
                    <b>{{ designRes.setting_ratio_pct }}</b> %
                  </el-descriptions-item>

                  <el-descriptions-item label="初撑力比校核">
                    <el-tag
                      :type="designRes.setting_ok ? 'success' : 'warning'"
                    >
                      {{ designRes.setting_ok ? '通过' : '超出建议区间' }}
                    </el-tag>
                  </el-descriptions-item>
                </template>
              </el-descriptions>

              <el-divider content-position="left">
                计算依据
              </el-divider>

              <el-descriptions
                :column="1"
                border
              >
                <el-descriptions-item label="缸径关系">
                  P = n × (π/4) × D² × p × η
                </el-descriptions-item>

                <el-descriptions-item label="标准化">
                  理论缸径向上圆整到程序内标准缸径系列
                </el-descriptions-item>

                <el-descriptions-item
                  v-if="designRes.rule"
                  label="初撑力比"
                >
                  {{ designRes.rule }}
                </el-descriptions-item>

                <el-descriptions-item label="来源">
                  {{ designRes.source }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>

            <EmptyState
              v-else
              title="等待缸径计算"
              description="输入工作阻力、承载立柱根数、立柱工作压力和历史修正系数 η 后执行计算。结果区将给出理论缸径、标准缸径及计算承载力。"
            />

          </el-col>

        </el-row>

        <!-- W35-D6: 最近计算记录，仅只读查看 -->
        <el-card
          shadow="never"
          style="margin-top: 18px"
        >
          <template #header>
            <div
              style="display: flex; justify-content: space-between; align-items: center"
            >
              <b>最近计算记录</b>

              <el-button
                size="small"
                :loading="recordListLoading"
                @click="loadRecentRecords"
              >
                刷新
              </el-button>
            </div>
          </template>

          <el-table
            v-loading="recordListLoading"
            :data="recordList"
            size="small"
            border
            style="width: 100%; cursor: pointer"
            @row-click="(row) => openRecordDetail(row.id)"
          >
            <el-table-column label="记录" width="90">
              <template #default="{ row }">
                #{{ row.id }}
              </template>
            </el-table-column>

            <el-table-column label="时间" min-width="170">
              <template #default="{ row }">
                {{ formatRecordTime(row.created_at) }}
              </template>
            </el-table-column>

            <el-table-column label="运行模式" width="110">
              <template #default="{ row }">
                {{ formatRunMode(row.run_mode) }}
              </template>
            </el-table-column>

            <el-table-column label="上下文来源" width="120">
              <template #default="{ row }">
                {{ formatContextSource(row.context_source_type) }}
              </template>
            </el-table-column>

            <el-table-column label="Formula ID" min-width="210">
              <template #default="{ row }">
                {{ row.formula_ids.join(' / ') }}
              </template>
            </el-table-column>

            <el-table-column label="操作" width="90">
              <template #default="{ row }">
                <el-button
                  link
                  type="primary"
                  @click.stop="openRecordDetail(row.id)"
                >
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <EmptyState
            v-if="!recordListLoading && recordList.length === 0"
            title="暂无计算记录"
            description="成功执行一次立柱设计后，计算记录将在这里显示。"
          />

          <el-drawer
            v-model="recordDrawerOpen"
            title="计算记录详情"
            size="720px"
          >
            <div v-loading="recordDetailLoading">
              <template v-if="recordDetail">
                <el-descriptions
                  :column="2"
                  border
                >
                  <el-descriptions-item label="记录编号">
                    #{{ recordDetail.id }}
                  </el-descriptions-item>

                  <el-descriptions-item label="时间">
                    {{ formatRecordTime(recordDetail.created_at) }}
                  </el-descriptions-item>

                  <el-descriptions-item label="运行模式">
                    {{ formatRunMode(recordDetail.run_mode) }}
                  </el-descriptions-item>

                  <el-descriptions-item label="上下文来源">
                    {{ formatContextSource(recordDetail.context_source_type) }}
                  </el-descriptions-item>

                  <el-descriptions-item label="上下文确认">
                    {{ formatConfirmed(recordDetail.context_confirmed) }}
                  </el-descriptions-item>

                  <el-descriptions-item label="记录版本">
                    {{ recordDetail.record_version }}
                  </el-descriptions-item>

                  <el-descriptions-item
                    label="Formula ID"
                    :span="2"
                  >
                    <el-tag
                      v-for="formulaId in recordDetail.formula_ids"
                      :key="formulaId"
                      type="info"
                      style="margin-right: 6px"
                    >
                      {{ formulaId }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>

                <el-divider content-position="left">
                  输入快照
                </el-divider>
                <pre style="white-space: pre-wrap; word-break: break-word">{{ prettyJson(recordDetail.inputs_snapshot) }}</pre>

                <el-divider content-position="left">
                  输出快照
                </el-divider>
                <pre style="white-space: pre-wrap; word-break: break-word">{{ prettyJson(recordDetail.outputs_snapshot) }}</pre>

                <el-divider content-position="left">
                  上下文快照
                </el-divider>
                <pre style="white-space: pre-wrap; word-break: break-word">{{ prettyJson(recordDetail.context_snapshot) }}</pre>
              </template>
            </div>
          </el-drawer>
        </el-card>

      </el-tab-pane>


      <!-- ==================================================
           B. 强度校核
           ================================================== -->
      <el-tab-pane label="强度校核" name="strength">

        <el-alert
          type="warning"
          :closable="false"
          show-icon
          title="当前许用应力采用 σs / n 作为计算脚手架，该口径仍需结合材料与液压缸设计标准复核；不得直接作为制造级壁厚设计依据。"
          class="strength-basis-warning"
        />

        <el-row :gutter="18">

          <el-col :xs="24" :lg="10">

            <el-card shadow="never">
              <template #header>
                <b>强度校核输入</b>
              </template>

              <el-form
                :model="strengthForm"
                label-width="155px"
              >

                <el-form-item label="材料">
                  <el-select
                    v-model="strengthForm.material"
                    style="width: 260px"
                  >
                    <el-option
                      label="27SiMn（σs=835 MPa，已核实）"
                      value="27SiMn"
                    />
                  </el-select>
                </el-form-item>

                <div class="material-note">
                  当前仅开放已核实材料。27SiMn 的 σb 暂无可靠核实值，
                  程序保持为空，不进行推测。
                </div>

                <el-form-item label="缸筒内径">
                  <el-input-number
                    v-model="strengthForm.d_mm"
                    :min="40"
                    :max="600"
                    :step="10"
                    controls-position="right"
                  />
                  <span class="unit">mm</span>
                </el-form-item>

                <el-form-item label="计算压力">
                  <el-input-number
                    v-model="strengthForm.p_mpa"
                    :min="1"
                    :max="400"
                    :step="0.5"
                    controls-position="right"
                  />
                  <span class="unit">MPa</span>
                </el-form-item>

                <el-form-item label="材料安全系数">
                  <el-input-number
                    v-model="strengthForm.material_safety_factor"
                    :min="1"
                    :max="5"
                    :step="0.1"
                    :precision="1"
                    controls-position="right"
                  />
                </el-form-item>

                <el-divider content-position="left">
                  应力校核（可选）
                </el-divider>

                <el-form-item label="启用应力校核">
                  <el-switch v-model="enableStress" />
                </el-form-item>

                <el-form-item
                  v-if="enableStress"
                  label="最大计算应力"
                >
                  <el-input-number
                    v-model="strengthForm.sigma_max_mpa"
                    :min="0"
                    :step="10"
                    controls-position="right"
                  />
                  <span class="unit">MPa</span>
                </el-form-item>

                <el-divider content-position="left">
                  压杆稳定（可选）
                </el-divider>

                <el-form-item label="启用稳定性校核">
                  <el-switch v-model="enableBuckling" />
                </el-form-item>

                <template v-if="enableBuckling">

                  <el-form-item label="弹性模量 E">
                    <el-input-number
                      v-model="strengthForm.e_mpa"
                      :min="1"
                      :step="1000"
                      controls-position="right"
                    />
                    <span class="unit">MPa</span>
                  </el-form-item>

                  <el-form-item label="截面惯性矩 I">
                    <el-input-number
                      v-model="strengthForm.i_mm4"
                      :min="1"
                      :step="1000000"
                      controls-position="right"
                    />
                    <span class="unit">mm⁴</span>
                  </el-form-item>

                  <el-form-item label="计算长度 L">
                    <el-input-number
                      v-model="strengthForm.l_mm"
                      :min="1"
                      :step="100"
                      controls-position="right"
                    />
                    <span class="unit">mm</span>
                  </el-form-item>

                  <el-form-item label="轴向载荷">
                    <el-input-number
                      v-model="strengthForm.load_kn"
                      :min="1"
                      :step="100"
                      controls-position="right"
                    />
                    <span class="unit">kN</span>
                  </el-form-item>

                  <el-form-item label="长度系数 μ">
                    <el-input-number
                      v-model="strengthForm.mu"
                      :min="0.1"
                      :step="0.1"
                      :precision="1"
                      controls-position="right"
                    />
                  </el-form-item>

                </template>

                <el-form-item>
                  <el-button
                    type="primary"
                    :loading="strengthLoading"
                    @click="runStrength"
                  >
                    开始校核
                  </el-button>

                  <el-button @click="fillStrengthExample">
                    填入校核示例
                  </el-button>

                  <el-button @click="clearStrength">
                    清空结果
                  </el-button>
                </el-form-item>

              </el-form>
            </el-card>

          </el-col>


          <el-col :xs="24" :lg="14">

            <el-card
              v-if="strengthRes"
              shadow="never"
            >
              <template #header>
                <b>校核结果</b>
              </template>

              <el-descriptions
                :column="2"
                border
              >
                <el-descriptions-item label="材料">
                  {{ strengthRes.material.name }}
                </el-descriptions-item>

                <el-descriptions-item label="屈服强度 σs">
                  {{ strengthRes.material.sigma_s_mpa }} MPa
                </el-descriptions-item>

                <el-descriptions-item label="抗拉强度 σb">
                  <el-tag
                    v-if="strengthRes.material.sigma_b_mpa === null"
                    type="info"
                  >
                    未核实，不使用
                  </el-tag>
                  <span v-else>
                    {{ strengthRes.material.sigma_b_mpa }} MPa
                  </span>
                </el-descriptions-item>

                <el-descriptions-item label="许用应力">
                  {{ strengthRes.material.sigma_allow_mpa }} MPa
                </el-descriptions-item>

                <el-descriptions-item label="理论壁厚">
                  <b>{{ strengthRes.wall.thickness_mm }}</b> mm
                </el-descriptions-item>

                <el-descriptions-item label="壁厚公式档">
                  <el-tag>
                    {{ regimeLabel(strengthRes.wall.regime) }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <el-divider content-position="left">
                应力校核
              </el-divider>

              <template v-if="strengthRes.stress">
                <el-descriptions
                  :column="2"
                  border
                >
                  <el-descriptions-item label="最大计算应力">
                    {{ strengthRes.stress.sigma_max_mpa }} MPa
                  </el-descriptions-item>

                  <el-descriptions-item label="安全系数">
                    {{ strengthRes.stress.safety_factor }}
                  </el-descriptions-item>

                  <el-descriptions-item label="判定">
                    <el-tag
                      :type="strengthRes.stress.ok ? 'success' : 'danger'"
                    >
                      {{ strengthRes.stress.ok ? '通过' : '不通过' }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </template>

              <el-alert
                v-else
                type="info"
                :closable="false"
                title="本次未启用材料应力校核"
              />

              <el-divider content-position="left">
                压杆稳定
              </el-divider>

              <template v-if="strengthRes.buckling">
                <el-descriptions
                  :column="2"
                  border
                >
                  <el-descriptions-item label="欧拉临界载荷">
                    {{ strengthRes.buckling.critical_load_kn }} kN
                  </el-descriptions-item>

                  <el-descriptions-item label="稳定安全系数">
                    {{ strengthRes.buckling.safety_factor }}
                  </el-descriptions-item>

                  <el-descriptions-item label="判定">
                    <el-tag
                      :type="strengthRes.buckling.ok ? 'success' : 'danger'"
                    >
                      {{ strengthRes.buckling.ok ? '通过' : '不通过' }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </template>

              <el-alert
                v-else
                type="info"
                :closable="false"
                title="本次未启用压杆稳定性校核"
              />

              <el-divider content-position="left">
                来源与边界
              </el-divider>

              <el-descriptions
                :column="1"
                border
              >
                <el-descriptions-item label="材料数据来源">
                  {{ strengthRes.material.source }}
                </el-descriptions-item>

                <el-descriptions-item label="壁厚公式来源">
                  {{ strengthRes.wall.source }}
                </el-descriptions-item>

                <el-descriptions-item label="边界说明">
                  {{ strengthRes.boundary_note }}
                </el-descriptions-item>
              </el-descriptions>

              <el-alert
                type="warning"
                :closable="false"
                show-icon
                class="example-warning"
              >
                <template #default>
                  当前复核示例中，43.4 MPa 和 656.7/835 MPa
                  来自已核实文献；欧拉稳定性所用 E、I、L、载荷
                  为公式验证构造参数，不代表与前述数据属于同一实际矿井工况。
                </template>
              </el-alert>

            </el-card>

            <EmptyState
              v-else
              title="等待强度校核"
              description="输入材料、缸径与计算压力后执行校核。可选启用材料应力与欧拉稳定性检查。"
            />

          </el-col>

        </el-row>

      </el-tab-pane>

    </el-tabs>

  </div>
</template>


<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  getCalculationRecord,
  getCalculationRecords,
  postColumnDesign,
  postColumnStrength,
} from '../api'

import FormulaCard from '../components/ui/FormulaCard.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import { clearDesignTransfer, readDesignTransfer, writeDesignTransfer } from '../utils/designTransfer'


const tab = ref('design')


// ============================================================
// 缸径设计
// ============================================================

const route = useRoute()

const transferRequested = [
  "selected_support",
  "calculated_requirement",
].includes(route.query.ctx)

const transferPayload =
  transferRequested
    ? readDesignTransfer()
    : null

const designContext = ref(
  transferPayload?.source_type === route.query.ctx
    ? transferPayload
    : null,
)

const contextConfirmed = ref(
  designContext.value == null ||
  designContext.value.confirmed === true,
)

const enableSetting = ref(false)
const designLoading = ref(false)
const designRes = ref(null)
const designExampleLoaded = ref(false)

const recordList = ref([])
const recordListLoading = ref(false)
const recordDrawerOpen = ref(false)
const recordDetailLoading = ref(false)
const recordDetail = ref(null)

const designForm = reactive({
  p_kn:
    designContext.value?.target?.resistance_kn
    ?? null,
  n: null,
  p_mpa: null,
  eta: null,
  p_set_kn: null,
})

const formatRecordTime = (value) => {
  if (!value) return '—'
  return String(value).replace('T', ' ')
}

const formatRunMode = (value) => {
  const map = {
    engineering: '工程计算',
    example: '计算示例',
  }
  return map[value] || value || '—'
}

const formatContextSource = (value) => {
  const map = {
    selected_support: '推荐支架',
    calculated_requirement: '需求计算',
    user_input: '用户输入',
  }
  return map[value] || value || '无上游上下文'
}

const formatConfirmed = (value) => {
  if (value === true) return '已确认'
  if (value === false) return '未确认'
  return '不适用'
}

const prettyJson = (value) => {
  if (value == null) return '—'
  return JSON.stringify(value, null, 2)
}


const loadRecentRecords = async () => {
  recordListLoading.value = true

  try {
    recordList.value = await getCalculationRecords({
      calc_type: 'column_design',
      limit: 20,
    })
  } catch (e) {
    // 全局 Axios 拦截器统一提示；保留已有列表。
  } finally {
    recordListLoading.value = false
  }
}

const openRecordDetail = async (recordId) => {
  recordDrawerOpen.value = true
  recordDetailLoading.value = true
  recordDetail.value = null

  try {
    recordDetail.value = await getCalculationRecord(recordId)
  } catch (e) {
    // 全局 Axios 拦截器统一提示。
  } finally {
    recordDetailLoading.value = false
  }
}


const designExampleIsCurrent = () =>
  designExampleLoaded.value === true &&
  designContext.value == null &&
  designForm.p_kn === 2533 &&
  designForm.n === 1 &&
  designForm.p_mpa === 31.5 &&
  designForm.eta === 1.0 &&
  enableSetting.value === true &&
  designForm.p_set_kn === 1900

const designReady = computed(() => {
  const required = [
    designForm.p_kn,
    designForm.n,
    designForm.p_mpa,
    designForm.eta,
  ]

  if (contextConfirmed.value === false) return false
  if (required.every(Number.isFinite) === false) return false
  if (
    enableSetting.value &&
    Number.isFinite(designForm.p_set_kn) === false
  ) {
    return false
  }

  return true
})

const confirmDesignContext = () => {
  contextConfirmed.value = true

  if (designContext.value != null) {
    designContext.value = {
      ...designContext.value,
      confirmed: true,
    }
    writeDesignTransfer(designContext.value)
  }
}


const fillDesignExample = () => {
  clearDesignTransfer()
  designContext.value = null
  contextConfirmed.value = true
  designExampleLoaded.value = true

  designForm.p_kn = 2533
  designForm.n = 1
  designForm.p_mpa = 31.5
  designForm.eta = 1.0
  designForm.p_set_kn = 1900
  enableSetting.value = true
  designRes.value = null
}


const clearDesign = () => {
  designRes.value = null
}


const runDesign = async () => {
  if (designReady.value === false) return

  designLoading.value = true

  try {
    const runMode =
      designExampleIsCurrent()
        ? "example"
        : "engineering"

    const payload = {
      p_kn: designForm.p_kn,
      n: designForm.n,
      p_mpa: designForm.p_mpa,
      eta: designForm.eta,
      run_mode: runMode,
      context_source_type:
        runMode === "example"
          ? null
          : (designContext.value?.source_type ?? null),
      context_confirmed:
        runMode === "example"
          ? null
          : (
              designContext.value != null
                ? contextConfirmed.value
                : null
            ),
      context_snapshot:
        runMode === "example"
          ? null
          : designContext.value,
    }

    if (enableSetting.value) {
      payload.p_set_kn = designForm.p_set_kn
    }

    // 项目Axios拦截器成功时已经返回 body.data，
    // 因此这里直接接计算结果，不再读取 r.code / r.data。
    designRes.value = await postColumnDesign(payload)
    loadRecentRecords()

  } catch (e) {
    // 全局Axios拦截器统一处理错误提示。
  } finally {
    designLoading.value = false
  }
}


loadRecentRecords()


// ============================================================
// 强度校核
// ============================================================

const enableStress = ref(true)
const enableBuckling = ref(true)

const strengthLoading = ref(false)
const strengthRes = ref(null)

const strengthForm = reactive({
  material: '27SiMn',

  d_mm: 200,
  p_mpa: 43.4,
  material_safety_factor: 2.0,

  sigma_max_mpa: 656.7,

  e_mpa: 206000,
  i_mm4: 10000000,
  l_mm: 2000,
  load_kn: 2000,
  mu: 1.0,
})


const fillStrengthExample = () => {
  strengthForm.material = '27SiMn'

  strengthForm.d_mm = 200
  strengthForm.p_mpa = 43.4
  strengthForm.material_safety_factor = 2.0

  strengthForm.sigma_max_mpa = 656.7

  strengthForm.e_mpa = 206000
  strengthForm.i_mm4 = 10000000
  strengthForm.l_mm = 2000
  strengthForm.load_kn = 2000
  strengthForm.mu = 1.0

  enableStress.value = true
  enableBuckling.value = true

  strengthRes.value = null
}


const clearStrength = () => {
  strengthRes.value = null
}


const runStrength = async () => {
  strengthLoading.value = true

  try {
    const payload = {
      d_mm: strengthForm.d_mm,
      p_mpa: strengthForm.p_mpa,
      material: strengthForm.material,
      material_safety_factor:
        strengthForm.material_safety_factor,
    }

    if (enableStress.value) {
      payload.sigma_max_mpa =
        strengthForm.sigma_max_mpa
    }

    if (enableBuckling.value) {
      payload.e_mpa = strengthForm.e_mpa
      payload.i_mm4 = strengthForm.i_mm4
      payload.l_mm = strengthForm.l_mm
      payload.load_kn = strengthForm.load_kn
      payload.mu = strengthForm.mu
    }

    strengthRes.value =
      await postColumnStrength(payload)

  } catch (e) {
    // 全局Axios拦截器统一处理错误提示。
  } finally {
    strengthLoading.value = false
  }
}


const regimeLabel = (regime) => {
  const map = {
    thin: '薄壁公式',
    mid: '中壁公式',
    thick: '厚壁/拉美公式',
  }

  return map[regime] || regime
}
</script>


<style scoped>
.column-view {
  width: 100%;
  max-width: 1450px;
  margin: 0 auto;
}

.page-head {
  margin-bottom: 16px;
}

.page-head h2 {
  margin: 0 0 6px;
  font-size: 22px;
}

.page-head p {
  margin: 0;
  color: #606266;
  line-height: 1.7;
}

.boundary-alert {
  margin-bottom: 18px;
}

.column-formula {
  margin-bottom: 18px;
}

.main-tabs {
  margin-top: 4px;
}

.strength-basis-warning {
  margin-bottom: 16px;
}

.unit {
  margin-left: 8px;
  color: #606266;
}

.material-note {
  margin: -6px 0 18px 155px;
  max-width: 520px;
  color: #909399;
  font-size: 13px;
  line-height: 1.6;
}

.example-warning {
  margin-top: 18px;
}

:deep(.el-input-number) {
  width: 220px;
}

:deep(.el-descriptions) {
  margin-bottom: 8px;
}

@media (max-width: 1200px) {
  .material-note {
    margin-left: 0;
  }
}
</style>
