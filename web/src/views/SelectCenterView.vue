<template>
  <div class="hs-page select-center">

    <PageHeader
      eyebrow="Selection Workspace"
      title="智能选型"
      description="根据工况条件与案例库进行候选液压支架匹配，并保留完整工况用于结果解释与后续设计计算。"
    >
      <StatusBadge
        label="案例驱动匹配"
        status="info"
      />
    </PageHeader>


    <section class="scope-card">

      <div class="scope-block core">

        <div class="scope-title">
          当前匹配核心输入
        </div>

        <p>
          当前候选匹配的核心特征为煤层厚度与煤层倾角。
          页面其他工况字段不会被静默计入相似度计算。
        </p>

        <div class="chips">
          <span class="chip core-chip">
            煤层厚度
          </span>

          <span class="chip core-chip">
            煤层倾角
          </span>
        </div>

      </div>


      <div class="scope-block">

        <div class="scope-title">
          工况档案与后续设计参数
        </div>

        <p>
          以下参数用于工况档案、结果解释、风险识别和后续设计模块；
          它们不等同于当前匹配算法的核心输入。
        </p>

        <div class="chips">
          <span class="chip">采高范围</span>
          <span class="chip">煤层硬度</span>
          <span class="chip">顶板类型</span>
          <span class="chip">底板比压</span>
          <span class="chip">矿压特征</span>
          <span class="chip">瓦斯</span>
          <span class="chip">埋深</span>
          <span class="chip">工作面长度</span>
        </div>

      </div>

    </section>


    <el-tabs
      v-model="active"
      class="selection-tabs"
    >
      <el-tab-pane
        label="表单输入"
        name="form"
      >
        <InputView />
      </el-tab-pane>

      <el-tab-pane
        label="选型向导"
        name="wizard"
        lazy
      >
        <WizardView />
      </el-tab-pane>

      <el-tab-pane
        label="对话选型"
        name="chat"
        lazy
      >
        <ChatView />
      </el-tab-pane>
    </el-tabs>

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

import InputView from './InputView.vue'
import WizardView from './WizardView.vue'
import ChatView from './ChatView.vue'

import PageHeader from '../components/ui/PageHeader.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'


const route = useRoute()
const router = useRouter()

const validTabs = [
  'form',
  'wizard',
  'chat',
]

const parseTab = (value) => {
  return validTabs.includes(value)
    ? value
    : 'form'
}

const active = ref(
  parseTab(route.query.tab)
)


watch(
  () => route.query.tab,
  (value) => {
    active.value = parseTab(value)
  }
)


watch(
  active,
  (value) => {
    if (route.query.tab === value) {
      return
    }

    router.replace({
      path: '/select',
      query: {
        ...route.query,
        tab: value,
      },
    })
  }
)
</script>


<style scoped>
.select-center {
  padding-bottom: 32px;
}


.scope-card {
  display: grid;
  grid-template-columns:
    minmax(0, 0.9fr)
    minmax(0, 1.4fr);

  margin-bottom: 20px;

  background: #fff;

  border: 1px solid var(--hs-gray-200);
  border-radius: var(--hs-radius-lg);
}


.scope-block {
  padding: 18px 20px;
}


.scope-block + .scope-block {
  border-left: 1px solid var(--hs-gray-200);
}


.scope-block.core {
  background: #f7fbff;

  border-radius:
    var(--hs-radius-lg)
    0
    0
    var(--hs-radius-lg);
}


.scope-title {
  color: var(--hs-gray-950);

  font-size: 13px;
  font-weight: 700;
}


.scope-block p {
  margin: 7px 0 12px;

  color: var(--hs-gray-600);

  font-size: 12px;
  line-height: 1.7;
}


.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}


.chip {
  display: inline-flex;

  padding: 4px 8px;

  color: var(--hs-gray-600);
  background: var(--hs-gray-050);

  border: 1px solid var(--hs-gray-200);
  border-radius: 5px;

  font-size: 11px;
  font-weight: 600;
}


.core-chip {
  color: #2867aa;
  background: #edf6ff;

  border-color: #bdd8f3;
}


.selection-tabs {
  padding: 0 18px 18px;

  background: #fff;

  border: 1px solid var(--hs-gray-200);
  border-radius: var(--hs-radius-lg);
}


/*
 * 子页面仍保留自己的历史标题。
 * 在 Selection Center 内由 PageHeader 统一负责页面标题。
 */
.select-center :deep(.el-tab-pane h2) {
  display: none;
}


@media (max-width: 1200px) {
  .scope-card {
    grid-template-columns: 1fr;
  }

  .scope-block + .scope-block {
    border-left: 0;
    border-top: 1px solid var(--hs-gray-200);
  }

  .scope-block.core {
    border-radius:
      var(--hs-radius-lg)
      var(--hs-radius-lg)
      0
      0;
  }
}
</style>
