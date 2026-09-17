<template>
  <div class="engineering-shell">

    <!-- =====================================================
         Sidebar
         ===================================================== -->
    <aside class="sidebar">

      <div class="brand">
        <div class="brand-mark">
          支
        </div>

        <div class="brand-copy">
          <strong>液压支架智能设计平台</strong>
          <span>HYDRAULIC SUPPORT ENGINEERING</span>
        </div>
      </div>


      <nav class="navigation">

        <template
          v-for="group in navGroups"
          :key="group.label"
        >

          <div class="nav-group">

            <div class="nav-group-title">
              <span>{{ group.label }}</span>

              <span
                v-if="group.planned"
                class="planned"
              >
                规划中
              </span>
            </div>

            <template v-if="group.items?.length">

              <button
                v-for="item in group.items"
                :key="item.path"
                class="nav-item"
                :class="{
                  active: isActive(item.path)
                }"
                type="button"
                @click="go(item.path)"
              >
                <span class="nav-indicator" />

                <span>{{ item.label }}</span>

                <span
                  v-if="item.legacy"
                  class="legacy"
                >
                  历史
                </span>
              </button>

            </template>

          </div>

        </template>

      </nav>


      <div class="sidebar-footer">
        <StatusBadge
          label="工程辅助原型"
          status="info"
        />

        <p>
          计算结果需结合标准、
          原始资料与工程条件复核。
        </p>
      </div>

    </aside>


    <!-- =====================================================
         Main shell
         ===================================================== -->
    <section class="shell-body">

      <header class="top-context">

        <div class="route-context">
          <span class="context-label">
            当前页面
          </span>

          <strong>
            {{ pageTitle }}
          </strong>
        </div>


        <div class="data-context">

          <div class="context-stat">
            <span>支架型号</span>
            <b>{{ stats.supports ?? '—' }}</b>
          </div>

          <div class="context-stat">
            <span>矿区</span>
            <b>{{ stats.areas ?? '—' }}</b>
          </div>

          <div class="context-stat">
            <span>案例</span>
            <b>{{ stats.cases ?? '—' }}</b>
          </div>

          <StatusBadge
            label="数据服务在线"
            :status="statsReady ? 'success' : 'neutral'"
          />

        </div>

      </header>


      <main class="shell-content">
        <router-view />
      </main>

    </section>

  </div>
</template>


<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  useRoute,
  useRouter,
} from 'vue-router'

import { getStats } from '../api'
import StatusBadge from '../components/ui/StatusBadge.vue'


const route = useRoute()
const router = useRouter()

const stats = ref({})
const statsReady = ref(false)


const navGroups = [
  {
    label: '工作台',
    items: [
      {
        label: '工程概览',
        path: '/workbench',
      },
    ],
  },

  {
    label: '智能选型',
    items: [
      {
        label: '选型中心',
        path: '/select',
      },
      {
        label: '推荐结果',
        path: '/result',
      },
      {
        label: '支架对比',
        path: '/compare',
      },
    ],
  },

  {
    label: '支架数据库',
    items: [
      {
        label: '矿区工况',
        path: '/areas',
      },
      {
        label: '矿区地图',
        path: '/map',
      },
      {
        label: '架型谱系',
        path: '/spectrum',
      },
      {
        label: '制造商',
        path: '/vendors',
      },
      {
        label: '数据质量',
        path: '/data-quality',
      },
    ],
  },

  {
    label: '设计计算',
    items: [
      {
        label: '计算中心',
        path: '/calc',
      },
    ],
  },

  {
    label: '图纸·模型·仿真',
    items: [],
    planned: true,
  },

  {
    label: '知识与证据',
    items: [],
    planned: true,
  },
]


const pageTitle = computed(
  () => route.meta?.title || '工程工作台'
)


const isActive = (path) => {
  return route.path === path
}


const go = (path) => {
  if (route.path !== path) {
    router.push(path)
  }
}


onMounted(async () => {
  try {
    stats.value = await getStats()
    statsReady.value = true
  } catch {
    statsReady.value = false
  }
})
</script>


<style scoped>
.engineering-shell {
  display: flex;

  min-height: 100vh;

  background: var(--hs-gray-050);
}


/* ============================================================
   Sidebar
   ============================================================ */

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;

  z-index: 30;

  display: flex;
  flex-direction: column;

  width: var(--hs-sidebar-width);

  background: var(--hs-navy-950);

  border-right: 1px solid
    rgba(255, 255, 255, 0.06);
}


.brand {
  display: flex;
  align-items: center;
  gap: 11px;

  min-height: 76px;

  padding: 15px 17px;

  border-bottom: 1px solid
    rgba(255, 255, 255, 0.08);
}


.brand-mark {
  display: flex;
  flex: 0 0 38px;
  align-items: center;
  justify-content: center;

  width: 38px;
  height: 38px;

  color: var(--hs-navy-950);
  background: var(--hs-orange-500);

  border-radius: 8px;

  font-size: 19px;
  font-weight: 800;
}


.brand-copy {
  min-width: 0;
}


.brand-copy strong {
  display: block;

  overflow: hidden;

  color: #fff;

  font-size: 14px;
  font-weight: 680;

  text-overflow: ellipsis;
  white-space: nowrap;
}


.brand-copy span {
  display: block;

  margin-top: 3px;

  color: #7890a7;

  font-size: 8px;
  letter-spacing: 0.05em;

  white-space: nowrap;
}


.navigation {
  flex: 1;

  overflow-y: auto;

  padding: 10px 10px 20px;
}


.nav-group {
  margin-bottom: 10px;
}


.nav-group-title {
  display: flex;
  align-items: center;
  justify-content: space-between;

  min-height: 30px;

  padding: 0 10px;

  color: #748ba1;

  font-size: 11px;
  font-weight: 700;

  letter-spacing: 0.06em;
}


.planned {
  padding: 2px 5px;

  color: #8096aa;

  background: rgba(255, 255, 255, 0.05);

  border-radius: 4px;

  font-size: 9px;
  font-weight: 500;

  letter-spacing: 0;
}


.nav-item {
  position: relative;

  display: flex;
  align-items: center;
  gap: 9px;

  width: 100%;
  min-height: 38px;

  margin: 2px 0;
  padding: 0 10px;

  color: #b7c6d5;
  background: transparent;

  border: 0;
  border-radius: 7px;

  cursor: pointer;

  font-family: inherit;
  font-size: 13px;
  text-align: left;

  transition:
    color var(--hs-transition),
    background var(--hs-transition);
}


.nav-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.055);
}


.nav-item.active {
  color: #fff;

  background: rgba(47, 128, 237, 0.17);

  font-weight: 650;
}


.nav-indicator {
  width: 3px;
  height: 18px;

  background: transparent;

  border-radius: 2px;
}


.nav-item.active .nav-indicator {
  background: var(--hs-blue-600);
}


.legacy {
  margin-left: auto;

  padding: 2px 5px;

  color: #d8a74a;
  background: rgba(243, 169, 59, 0.09);

  border-radius: 4px;

  font-size: 9px;
}


.sidebar-footer {
  padding: 14px 16px 16px;

  border-top: 1px solid
    rgba(255, 255, 255, 0.07);
}


.sidebar-footer p {
  margin: 9px 0 0;

  color: #748ba1;

  font-size: 10px;
  line-height: 1.55;
}


/* ============================================================
   Main
   ============================================================ */

.shell-body {
  width: calc(
    100% - var(--hs-sidebar-width)
  );

  min-width: 0;

  margin-left: var(--hs-sidebar-width);
}


.top-context {
  position: sticky;
  top: 0;

  z-index: 20;

  display: flex;
  align-items: center;
  justify-content: space-between;

  height: var(--hs-topbar-height);

  padding: 0 24px;

  background: rgba(255, 255, 255, 0.97);

  border-bottom: 1px solid var(--hs-gray-200);
}


.route-context {
  display: flex;
  flex-direction: column;
  gap: 2px;
}


.context-label {
  color: var(--hs-gray-500);

  font-size: 10px;
}


.route-context strong {
  color: var(--hs-gray-950);

  font-size: 15px;
  font-weight: 680;
}


.data-context {
  display: flex;
  align-items: center;
  gap: 20px;
}


.context-stat {
  display: flex;
  align-items: baseline;
  gap: 6px;

  padding-right: 18px;

  border-right: 1px solid var(--hs-gray-200);
}


.context-stat span {
  color: var(--hs-gray-500);

  font-size: 11px;
}


.context-stat b {
  color: var(--hs-navy-900);

  font-size: 14px;
}


.shell-content {
  width: 100%;

  padding: 24px 26px 56px;
}


@media (max-width: 1366px) {
  .data-context {
    gap: 12px;
  }

  .context-stat {
    padding-right: 12px;
  }

  .shell-content {
    padding: 20px 20px 48px;
  }
}
</style>
