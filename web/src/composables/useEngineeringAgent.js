import { ref } from 'vue'
import { marked } from 'marked'

import { streamChat, postMatch } from '../api'
import { useChatStore } from '../store/chat'


// ============================================================
// Shared runtime
//
// AgentDock 与兼容 ChatView 共用这一套运行状态，避免同时创建
// 两个独立流式请求控制器。
// ============================================================

const sending = ref(false)
const lastMeta = ref(null)
const lastStage = ref('')

let controller = null
let stopRequested = false


export function useEngineeringAgent() {
  const store = useChatStore()


  const renderMd = (text) => {
    try {
      return marked.parse(
        text || '',
        { async: false },
      )
    } catch {
      return String(text || '')
        .replace(/\n/g, '<br>')
    }
  }


  const stop = () => {
    if (!controller) {
      return
    }

    stopRequested = true
    controller.abort()
  }


  const clear = () => {
    stop()

    store.clear()

    lastMeta.value = null
    lastStage.value = ''
  }


  const send = async (rawText) => {
    const text = String(rawText || '').trim()

    if (!text || sending.value) {
      return
    }

    stopRequested = false
    lastMeta.value = null
    lastStage.value = ''

    store.pushUser(text)

    const temp = {
      role: 'assistant',
      text: '',
    }

    store.messages.push(temp)

    sending.value = true
    controller = new AbortController()

    try {
      await streamChat(
        {
          message: text,
          session_id: store.sessionId,
        },
        {
          onChunk: chunk => {
            temp.text += chunk
          },

          onMeta: meta => {
            lastMeta.value = meta
            lastStage.value =
              meta.stage || ''

            if (meta.session_id) {
              store.setSession(
                meta.session_id,
              )
            }
          },

          signal: controller.signal,
        },
      )
    } catch (e) {
      if (!stopRequested) {
        temp.text =
          '请求失败：' +
          (e.message || e)
      }
    } finally {
      controller = null
      sending.value = false

      if (
        !stopRequested
        && lastMeta.value?.stage
          === 'explained'
      ) {
        const p =
          lastMeta.value.params || {}

        const payload = {
          coal_thickness:
            Number(
              p.coal_thickness,
            ),

          dip_angle:
            Number(
              p.dip_angle,
            ) || 0,

          top_n: 3,
        }

        try {
          const result =
            await postMatch(payload)

          store.pushCard({
            items:
              (result.items || [])
                .map(item => ({
                  model:
                    item.support_model,

                  similarity:
                    Math.round(
                      (
                        item.similarity
                        ?? 0
                      ) * 100,
                    ),

                  resistance:
                    item
                      .working_resistance,

                  intensity:
                    item.intensity,
                })),

            total: result.total,
          })
        } catch {
          // 推荐卡失败不影响对话主体。
        }
      }

      stopRequested = false
    }
  }


  return {
    store,

    sending,
    lastMeta,
    lastStage,

    renderMd,
    send,
    stop,
    clear,
  }
}
