<template>
  <div class="hs-page">

    <PageHeader
      eyebrow="Engineering Workspace"
      title="工程工作台"
      description="液压支架选型、参数设计、数据治理与工程分析的统一入口。"
    >
      <StatusBadge
        label="系统基线稳定"
        status="success"
      />
    </PageHeader>


    <section class="metrics">
      <MetricCard
        label="支架型号"
        :value="stats.supports"
        note="当前数据库记录"
        status="success"
      />

      <MetricCard
        label="矿区工况"
        :value="stats.areas"
        note="前台可用矿区"
        status="success"
      />

      <MetricCard
        label="工况案例"
        :value="stats.cases"
        note="案例与盲测基线"
        status="success"
      />

      <MetricCard
        label="支护强度覆盖率"
        :value="stats.intensity_coverage"
        unit="%"
        note="型号参数完整度指标"
        status="success"
      />

      <MetricCard
        label="质量覆盖率"
        :value="stats.weight_coverage"
        unit="%"
        note="当前仍属于薄弱字段"
        status="warning"
      />
    </section>


    <section class="hs-page-section">

      <h2 class="hs-section-title">
        工程入口
      </h2>

      <div class="module-grid">

        <button
          v-for="m in modules"
          :key="m.title"
          class="module-card"
          type="button"
          :disabled="!m.path"
          @click="open(m.path)"
        >
          <div class="module-index">
            {{ m.index }}
          </div>

          <div>
            <strong>
              {{ m.title }}
            </strong>

            <p>
              {{ m.description }}
            </p>

            <span
              v-if="!m.path"
              class="module-state"
            >
              规划中
            </span>

            <span
              v-else
              class="module-link"
            >
              进入模块 →
            </span>
          </div>
        </button>

      </div>

    </section>


    <section class="hs-page-section">
      <el-alert
        type="info"
        :closable="false"
        show-icon
      >
        当前平台定位为工程设计辅助原型。
        计算值、估算值和来源数据将逐步通过 Formula ID、
        Source Badge 与证据链统一管理。
      </el-alert>
    </section>

  </div>
</template>


<script setup>
import {
  onMounted,
  ref,
} from 'vue'

import { useRouter } from 'vue-router'

import { getStats } from '../api'

import PageHeader from '../components/ui/PageHeader.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'


const router = useRouter()
const stats = ref({})


const modules = [
  {
    index: '01',
    title: '智能选型',
    description:
      '输入工况、案例匹配、候选推荐与支架对比。',
    path: '/select',
  },
  {
    index: '02',
    title: '支架数据库',
    description:
      '矿区、架型谱系、制造商与参数完整度。',
    path: '/areas',
  },
  {
    index: '03',
    title: '设计计算',
    description:
      '支护需求、立柱设计与后续液压系统计算。',
    path: '/calc',
  },
  {
    index: '04',
    title: '图纸·模型·仿真',
    description:
      '二维、三维、机构运动和液压动态分析。',
    path: '',
  },
  {
    index: '05',
    title: '知识与证据',
    description:
      '公式、来源、参数证据和计算审计。',
    path: '',
  },
]


const open = (path) => {
  if (path) {
    router.push(path)
  }
}


onMounted(async () => {
  try {
    stats.value = await getStats()
  } catch {
    stats.value = {}
  }
})
</script>


<style scoped>
.metrics {
  display: grid;
  grid-template-columns:
    repeat(5, minmax(0, 1fr));
  gap: 12px;
}


.module-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 14px;
}


.module-card {
  display: flex;
  gap: 14px;

  min-height: 145px;

  padding: 19px;

  color: inherit;
  background: #fff;

  border: 1px solid var(--hs-gray-200);
  border-radius: var(--hs-radius-lg);

  cursor: pointer;

  font-family: inherit;
  text-align: left;

  transition:
    border-color var(--hs-transition),
    box-shadow var(--hs-transition);
}


.module-card:not(:disabled):hover {
  border-color: #b9d2e9;
  box-shadow: var(--hs-shadow-md);
}


.module-card:disabled {
  cursor: default;
  opacity: 0.72;
}


.module-index {
  color: var(--hs-orange-500);

  font-size: 12px;
  font-weight: 800;

  letter-spacing: 0.06em;
}


.module-card strong {
  color: var(--hs-navy-900);

  font-size: 16px;
}


.module-card p {
  min-height: 42px;

  margin: 9px 0 14px;

  color: var(--hs-gray-600);

  font-size: 13px;
  line-height: 1.65;
}


.module-link {
  color: var(--hs-blue-600);

  font-size: 12px;
  font-weight: 650;
}


.module-state {
  color: var(--hs-gray-500);

  font-size: 12px;
}


@media (max-width: 1366px) {
  .metrics {
    grid-template-columns:
      repeat(3, minmax(0, 1fr));
  }
}
</style>
