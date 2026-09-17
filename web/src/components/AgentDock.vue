<template>
  <div class="agent-dock-root">
    <button
      v-if="!open"
      class="agent-launcher"
      type="button"
      @click="openDock"
    >
      <span class="launcher-mark">
        AI
      </span>

      <span>
        工程助手
      </span>
    </button>

    <aside
      v-else
      class="agent-dock"
      :class="{
        minimized,
      }"
    >
      <header
        class="dock-head"
        @dblclick="
          minimized =
            !minimized
        "
      >
        <div class="dock-title">
          <div class="dock-mark">
            AI
          </div>

          <div>
            <strong>
              液压支架助手
            </strong>

            <span>
              当前能力：工况问答与选型
            </span>
          </div>
        </div>

        <div class="dock-actions">
          <button
            type="button"
            :title="
              minimized
                ? '展开'
                : '最小化'
            "
            @click.stop="
              minimized =
                !minimized
            "
          >
            {{
              minimized
                ? '□'
                : '—'
            }}
          </button>

          <button
            type="button"
            title="关闭"
            @click.stop="closeDock"
          >
            ×
          </button>
        </div>
      </header>

      <AgentConversation
        v-show="!minimized"
        :context-label="
          contextLabel
        "
        compact
      />
    </aside>
  </div>
</template>


<script setup>
import { ref } from 'vue'

import AgentConversation
  from './AgentConversation.vue'


defineProps({
  contextLabel: {
    type: String,
    default: '',
  },
})


const open = ref(false)
const minimized = ref(false)


const openDock = () => {
  open.value = true
  minimized.value = false
}


const closeDock = () => {
  open.value = false
  minimized.value = false
}
</script>


<style scoped>
.agent-launcher {
  position: fixed;
  right: 22px;
  bottom: 22px;
  z-index: 80;

  display: flex;
  align-items: center;
  gap: 8px;

  min-height: 42px;
  padding: 0 14px 0 9px;

  color: #fff;
  background: #123b61;
  border: 1px solid
    rgba(255, 255, 255, .12);
  border-radius: 22px;

  box-shadow:
    0 7px 22px
    rgba(18, 59, 97, .25);

  cursor: pointer;
  font-family: inherit;
  font-size: 12px;
  font-weight: 650;
}

.launcher-mark,
.dock-mark {
  display: flex;
  align-items: center;
  justify-content: center;

  width: 28px;
  height: 28px;

  color: #123b61;
  background: #f3a93b;

  border-radius: 7px;

  font-size: 10px;
  font-weight: 800;
}

.agent-dock {
  position: fixed;
  top: 76px;
  right: 18px;
  bottom: 18px;

  z-index: 80;

  display: flex;
  flex-direction: column;

  width: 410px;

  overflow: hidden;

  background: #fff;
  border: 1px solid #dce3ea;
  border-radius: 11px;

  box-shadow:
    0 16px 46px
    rgba(24, 48, 72, .18);
}

.agent-dock.minimized {
  top: auto;
  bottom: 22px;

  width: 310px;
  height: 54px;
}

.dock-head {
  display: flex;
  flex: none;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  min-height: 54px;
  padding: 8px 9px 8px 11px;

  background: #fff;
  border-bottom: 1px solid #e5e9ee;
}

.minimized .dock-head {
  border-bottom: 0;
}

.dock-title {
  display: flex;
  align-items: center;
  gap: 9px;

  min-width: 0;
}

.dock-title > div:last-child {
  display: grid;
  min-width: 0;
  gap: 2px;
}

.dock-title strong {
  overflow: hidden;

  color: #17324d;

  font-size: 13px;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.dock-title span {
  overflow: hidden;

  color: #7b8493;

  font-size: 10px;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.dock-actions {
  display: flex;
  gap: 3px;
}

.dock-actions button {
  width: 30px;
  height: 30px;

  color: #667085;
  background: transparent;

  border: 0;
  border-radius: 6px;

  cursor: pointer;
  font-size: 17px;
}

.dock-actions button:hover {
  color: #17324d;
  background: #f2f5f8;
}

@media (max-width: 768px) {
  .agent-dock {
    top: 12px;
    right: 12px;
    bottom: 12px;

    width:
      calc(100vw - 24px);
  }

  .agent-dock.minimized {
    right: 12px;
    bottom: 12px;

    width:
      min(
        310px,
        calc(100vw - 24px)
      );
  }
}
</style>
