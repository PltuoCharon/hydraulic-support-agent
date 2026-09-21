<template>
  <div class="hs-page calc-center">
    <PageHeader
      eyebrow="Engineering Calculation"
      title="设计计算"
      description="围绕支护需求、立柱与千斤顶参数进行参数化工程计算与校核。"
    >
      <StatusBadge
        label="参数化设计辅助"
        status="info"
      />
    </PageHeader>

    <section class="calc-boundary">
      <div>
        <strong>计算边界</strong>
        <p>
          当前模块用于公式复现、参数设计辅助和方案比较；
          不生成结构设计图样，也不直接替代制造级设计审查。
        </p>
      </div>

      <StatusBadge
        label="非制造设计依据"
        status="warning"
      />
    </section>

    <nav class="module-nav">
      <button
        v-for="item in modules"
        :key="item.key"
        class="module-item"
        :class="{
          active: mod === item.key,
          disabled: item.disabled,
        }"
        :disabled="item.disabled"
        @click="selectModule(item)"
      >
        <span class="module-index">
          {{ item.index }}
        </span>

        <span class="module-copy">
          <strong>{{ item.label }}</strong>
          <small>{{ item.description }}</small>
        </span>

        <span
          v-if="item.disabled"
          class="planned"
        >
          计划中
        </span>
      </button>
    </nav>

    <section class="module-stage">
      <QNeedView
        v-if="mod === 'qneed'"
      />

      <ColumnView
        v-else-if="mod === 'column'"
      />

      <JackView
        v-else-if="mod === 'jack'"
      />

      <EmptyState
        v-else
        title="该计算模块尚未开放"
        description="当前版本先完成支护需求与立柱设计校核，其他液压系统模块将在证据和公式完成核验后接入。"
      />
    </section>
  </div>
</template>

<script setup>
import {
  ref,
  watch,
} from 'vue'

import {
  useRoute,
  useRouter,
} from 'vue-router'

import QNeedView from './QNeedView.vue'
import ColumnView from './ColumnView.vue'
import JackView from './JackView.vue'

import PageHeader from '../components/ui/PageHeader.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'
import EmptyState from '../components/ui/EmptyState.vue'


const route = useRoute()
const router = useRouter()


const validModules = [
  'qneed',
  'column',
  'jack',
]


const parseModule = (value) =>
  validModules.includes(value)
    ? value
    : 'qneed'


const mod = ref(
  parseModule(route.query.m)
)


const modules = [
  {
    index: '01',
    key: 'qneed',
    label: '支护需求',
    description: '计算需求支护强度 q_need',
  },
  {
    index: '02',
    key: 'column',
    label: '立柱设计与校核',
    description: '缸径、壁厚、应力与稳定性',
  },
  {
    index: '03',
    key: 'jack',
    label: '千斤顶设计',
    description: '推移千斤顶参数设计与校核',
  },
  {
    index: '04',
    key: 'valve',
    label: '阀组设计',
    description: '压力、流量与安全阀匹配',
    disabled: true,
  },
  {
    index: '05',
    key: 'pump',
    label: '泵站匹配',
    description: '系统压力与供液能力',
    disabled: true,
  },
]


const selectModule = (item) => {
  if (item.disabled) {
    return
  }

  mod.value = item.key
}


watch(
  () => route.query.m,
  value => {
    mod.value = parseModule(value)
  },
)


watch(
  mod,
  value => {
    if (route.query.m === value) {
      return
    }

    router.replace({
      query: {
        ...route.query,
        m: value,
      },
    })
  },
)
</script>

<style scoped>
.calc-center {
  display: grid;
  gap: 18px;
}

.calc-boundary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 15px 18px;
  background: #fff;
  border: 1px solid #e1e7ed;
  border-radius: 9px;
}

.calc-boundary strong {
  color: #17324d;
  font-size: 14px;
}

.calc-boundary p {
  margin: 4px 0 0;
  color: #667085;
  font-size: 12px;
  line-height: 1.6;
}

.module-nav {
  display: grid;
  grid-template-columns:
    repeat(5, minmax(0, 1fr));
  gap: 10px;
}

.module-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 11px;
  min-height: 82px;
  padding: 13px;
  text-align: left;
  background: #fff;
  border: 1px solid #dfe5eb;
  border-radius: 8px;
  cursor: pointer;
  transition: .15s ease;
}

.module-item:hover:not(.disabled) {
  border-color: #8bbaf2;
}

.module-item.active {
  background: #f5f9fe;
  border-color: #2f80ed;
  box-shadow:
    inset 0 0 0 1px #2f80ed;
}

.module-item.disabled {
  cursor: not-allowed;
  opacity: .55;
}

.module-index {
  color: #8a94a3;
  font-family: Consolas, monospace;
  font-size: 11px;
}

.module-copy {
  display: grid;
  gap: 5px;
}

.module-copy strong {
  color: #17324d;
  font-size: 13px;
}

.module-copy small {
  color: #7b8493;
  font-size: 11px;
  line-height: 1.45;
}

.planned {
  position: absolute;
  top: 8px;
  right: 8px;
  color: #8a94a3;
  font-size: 10px;
}

.module-stage {
  min-width: 0;
}

@media (max-width: 1280px) {
  .module-nav {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }
}
</style>
