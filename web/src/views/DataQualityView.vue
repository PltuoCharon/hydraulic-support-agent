<template>
  <div class="hs-page quality-page">
    <PageHeader
      eyebrow="Data Governance"
      title="数据质量"
      description="集中查看数据状态、字段完整度、缺失项与来源治理状态。字段有值不等于数据正确，也不等于工程可信。"
    >
      <StatusBadge
        label="字段完整度 ≠ 工程可信度"
        status="warning"
      />
    </PageHeader>

    <section
      v-if="quality"
      class="metric-grid"
    >
      <MetricCard
        label="数据库总型号"
        :value="quality.supports.total"
        note="全部 support_models"
      />

      <MetricCard
        label="Verified"
        :value="quality.supports.verified"
        note="默认参与工程分析"
      />

      <MetricCard
        label="Suspect"
        :value="quality.supports.suspect"
        note="默认不参与分析"
      />

      <MetricCard
        label="含估算/复算标记"
        :value="quality.supports.estimated_rows"
        note="来源摘要含估算标记，不等同于低质量"
      />
    </section>

    <el-alert
      v-if="quality"
      title="完整度口径：known 仅表示字段非空；页面不对数据真实性、准确性或制造级可用性进行评分。"
      type="info"
      :closable="false"
      show-icon
    />

    <section
      v-if="quality"
      class="quality-grid"
    >
      <div class="engineering-panel">
        <div class="panel-head">
          <div>
            <h3>支架库字段完整度</h3>
            <p>
              基数：
              {{ quality.supports.verified }}
              个 verified 型号。
            </p>
          </div>
        </div>

        <div
          v-for="item in quality.supports.verified_fields"
          :key="item.key"
          class="field-row"
        >
          <div class="field-head">
            <span>{{ item.label }}</span>

            <strong>
              {{ item.known }} / {{ item.total }}
            </strong>
          </div>

          <el-progress
            :percentage="item.coverage"
            :stroke-width="8"
          />

          <div class="field-foot">
            <span>
              覆盖率 {{ item.coverage }}%
            </span>

            <span>
              缺失 {{ item.missing }}
            </span>
          </div>
        </div>
      </div>

      <div class="engineering-panel">
        <div class="panel-head">
          <div>
            <h3>矿区工况字段完整度</h3>
            <p>
              基数：
              {{ quality.areas.total }}
              个前台可用矿区，不含盲测。
            </p>
          </div>
        </div>

        <div
          v-for="item in quality.areas.fields"
          :key="item.key"
          class="field-row"
        >
          <div class="field-head">
            <span>{{ item.label }}</span>

            <strong>
              {{ item.known }} / {{ item.total }}
            </strong>
          </div>

          <el-progress
            :percentage="item.coverage"
            :stroke-width="8"
          />

          <div class="field-foot">
            <span>
              覆盖率 {{ item.coverage }}%
            </span>

            <span>
              缺失 {{ item.missing }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <section
      v-if="quality"
      class="engineering-panel governance-panel"
    >
      <div class="panel-head">
        <div>
          <h3>来源与证据治理</h3>
          <p>
            当前 source 仅保存主要来源摘要；
            参数级证据仍需独立 provenance 结构。
          </p>
        </div>

        <StatusBadge
          :label="sourceSchemaLabel"
          status="warning"
        />
      </div>

      <div class="governance-grid">
        <div class="governance-item">
          <span>当前字段</span>
          <strong>support_models.source</strong>
        </div>

        <div class="governance-item">
          <span>数据库类型</span>
          <strong>
            {{ quality.source_schema.data_type }}
            ({{ quality.source_schema.max_length }})
          </strong>
        </div>

        <div class="governance-item">
          <span>当前职责</span>
          <strong>主要来源摘要</strong>
        </div>

        <div class="governance-item">
          <span>后续治理</span>
          <strong>参数级 provenance</strong>
        </div>
      </div>

      <el-alert
        title="不要继续把论文题名、页码、估算说明、补录历史全部拼接到 source 字段。后续应拆分参数级证据表。"
        type="warning"
        :closable="false"
        show-icon
      />

      <div class="notes">
        <p
          v-for="note in quality.notes"
          :key="note"
        >
          {{ note }}
        </p>
      </div>
    </section>
  </div>
</template>

<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import { getDataQuality } from '../api'

import PageHeader from '../components/ui/PageHeader.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'


const quality = ref(null)


const sourceSchemaLabel = computed(() => {
  if (!quality.value) {
    return '来源结构'
  }

  const schema =
    quality.value.source_schema

  return `${schema.data_type}(${schema.max_length})`
})


onMounted(async () => {
  quality.value =
    await getDataQuality()
})
</script>

<style scoped>
.quality-page {
  display: grid;
  gap: 18px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.quality-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.engineering-panel {
  padding: 20px;
  background: #fff;
  border: 1px solid var(--hs-gray-200, #e5e7eb);
  border-radius: var(--hs-radius-lg, 10px);
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 18px;
}

.panel-head h3 {
  margin: 0 0 6px;
  font-size: 17px;
}

.panel-head p {
  margin: 0;
  color: #667085;
  font-size: 13px;
  line-height: 1.6;
}

.field-row {
  padding: 13px 0;
  border-bottom: 1px solid #eef1f4;
}

.field-row:last-child {
  border-bottom: 0;
}

.field-head,
.field-foot {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.field-head {
  margin-bottom: 8px;
  font-size: 14px;
}

.field-head strong {
  color: #123B61;
}

.field-foot {
  margin-top: 5px;
  color: #7b8493;
  font-size: 12px;
}

.governance-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.governance-item {
  display: grid;
  gap: 6px;
  padding: 14px;
  background: #f7f9fb;
  border: 1px solid #edf0f3;
  border-radius: 8px;
}

.governance-item span {
  color: #667085;
  font-size: 12px;
}

.governance-item strong {
  color: #25364a;
  font-size: 14px;
}

.notes {
  margin-top: 14px;
  color: #667085;
  font-size: 13px;
  line-height: 1.7;
}

.notes p {
  margin: 4px 0;
}

@media (max-width: 1200px) {
  .metric-grid,
  .quality-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .governance-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
