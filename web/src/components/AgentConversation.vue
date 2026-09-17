<template>
  <div
    class="agent-conversation"
    :class="{
      compact,
    }"
  >
    <div
      v-if="contextLabel"
      class="agent-context"
    >
      <span>当前页面</span>
      <strong>
        {{ contextLabel }}
      </strong>
    </div>

    <div
      ref="listEl"
      class="agent-list"
    >
      <div
        v-if="!store.messages.length"
        class="agent-empty"
      >
        <strong>开始工程对话</strong>

        <p>
          当前已接入工况问答与液压支架选型能力。
        </p>
      </div>

      <div
        v-for="(message, index)
          in store.messages"
        :key="index"
        class="message-row"
        :class="message.role"
      >
        <div
          class="message-bubble"
          :class="message.role"
        >
          <span
            v-if="
              message.role === 'user'
            "
          >
            {{ message.text }}
          </span>

          <div
            v-else-if="message.card"
            class="recommendation-card"
          >
            <div class="rec-title">
              推荐结果
              <small>
                相似工况
                {{ message.card.total }}
                个
              </small>
            </div>

            <div
              v-for="(
                item,
                itemIndex
              ) in message.card.items"
              :key="item.model"
              class="rec-item"
            >
              <div>
                <strong>
                  #{{ itemIndex + 1 }}
                  {{ item.model }}
                </strong>

                <span>
                  相似度
                  {{ item.similarity }}%
                </span>
              </div>

              <div class="rec-data">
                <span>
                  {{
                    item.resistance
                      != null
                      ? `${item.resistance} kN`
                      : '工作阻力 —'
                  }}
                </span>

                <span>
                  {{
                    item.intensity
                      != null
                      ? `${item.intensity} MPa`
                      : '支护强度 —'
                  }}
                </span>
              </div>
            </div>

            <el-button
              size="small"
              type="primary"
              @click="
                router.push('/result')
              "
            >
              查看推荐结果
            </el-button>
          </div>

          <div
            v-else
            class="assistant-text"
            v-html="
              renderMd(
                message.text,
              )
            "
          />
        </div>
      </div>
    </div>

    <el-alert
      v-if="
        lastStage
          === 'confirm_pending'
      "
      type="warning"
      :closable="false"
      show-icon
      class="confirm-alert"
      title="参数已收集，请回复「对」确认；也可以直接补充或修改工况参数。"
    />

    <div class="agent-input">
      <el-input
        v-model="input"
        placeholder="输入工况或选型问题"
        :disabled="sending"
        clearable
        @keyup.enter="submit"
      />

      <el-button
        v-if="sending"
        type="warning"
        plain
        @click="stop"
      >
        停止
      </el-button>

      <el-button
        v-else
        type="primary"
        :disabled="!input.trim()"
        @click="submit"
      >
        发送
      </el-button>

      <el-button
        :disabled="sending"
        @click="clear"
      >
        清空
      </el-button>
    </div>
  </div>
</template>


<script setup>
import {
  nextTick,
  onMounted,
  ref,
  watch,
} from 'vue'

import {
  useRouter,
} from 'vue-router'

import {
  useEngineeringAgent,
} from '../composables/useEngineeringAgent'


defineProps({
  contextLabel: {
    type: String,
    default: '',
  },

  compact: {
    type: Boolean,
    default: false,
  },
})


const router = useRouter()

const input = ref('')
const listEl = ref(null)


const {
  store,

  sending,
  lastStage,

  renderMd,
  send,
  stop,
  clear,
} = useEngineeringAgent()


const scrollBottom = async () => {
  await nextTick()

  if (listEl.value) {
    listEl.value.scrollTop =
      listEl.value.scrollHeight
  }
}


const submit = async () => {
  const text = input.value.trim()

  if (!text || sending.value) {
    return
  }

  input.value = ''

  await send(text)
}


watch(
  () => store.messages,
  scrollBottom,
  {
    deep: true,
  },
)


onMounted(
  scrollBottom,
)
</script>


<style scoped>
.agent-conversation {
  display: flex;
  flex: 1;
  min-height: 0;
  flex-direction: column;
}

.agent-context {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 11px;
  color: #667085;
  background: #f7f9fb;
  border-bottom: 1px solid #e7ebef;
  font-size: 11px;
}

.agent-context strong {
  overflow: hidden;
  color: #344054;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.agent-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 14px;
  background: #f5f7fa;
}

.agent-empty {
  padding: 50px 20px;
  color: #667085;
  text-align: center;
}

.agent-empty strong {
  color: #344054;
  font-size: 14px;
}

.agent-empty p {
  margin: 7px 0 0;
  font-size: 12px;
}

.message-row {
  display: flex;
  margin-bottom: 11px;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 86%;
  padding: 9px 11px;
  border-radius: 9px;
  font-size: 13px;
  line-height: 1.65;
  word-break: break-word;
}

.message-bubble.user {
  color: #fff;
  background: #123b61;
  border-top-right-radius: 2px;
}

.message-bubble.assistant {
  color: #303133;
  background: #fff;
  border: 1px solid #e6ebf0;
  border-top-left-radius: 2px;
}

.assistant-text :deep(p) {
  margin: 4px 0;
}

.assistant-text :deep(ul),
.assistant-text :deep(ol) {
  margin: 5px 0;
  padding-left: 19px;
}

.assistant-text :deep(li) {
  margin: 2px 0;
}

.assistant-text :deep(pre) {
  overflow-x: auto;
  margin: 7px 0;
  padding: 9px;
  background: #f5f7fa;
  border-radius: 6px;
}

.assistant-text :deep(code) {
  padding: 1px 4px;
  background: #f5f7fa;
  border-radius: 3px;
  font-family:
    Consolas,
    Monaco,
    monospace;
}

.recommendation-card {
  display: grid;
  gap: 9px;
  min-width: 270px;
}

.rec-title {
  color: #17324d;
  font-weight: 700;
}

.rec-title small {
  margin-left: 6px;
  color: #667085;
  font-weight: 400;
}

.rec-item {
  display: grid;
  gap: 5px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #d9e2ec;
}

.rec-item > div {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.rec-item span {
  color: #667085;
  font-size: 11px;
}

.rec-data {
  justify-content: flex-start !important;
}

.confirm-alert {
  margin: 8px 10px 0;
}

.agent-input {
  display: grid;
  grid-template-columns:
    minmax(0, 1fr)
    auto
    auto;
  gap: 7px;
  padding: 10px;
  background: #fff;
  border-top: 1px solid #e2e7ec;
}

.compact .agent-list {
  padding: 11px;
}

.compact .message-bubble {
  max-width: 92%;
}
</style>
