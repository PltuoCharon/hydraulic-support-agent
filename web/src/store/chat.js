import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
  state: () => ({
    sessionId: null,
    messages: [
      {
        role: 'assistant',
        text: '你好，我是选型助手。告诉我工况条件（煤层厚度、倾角、瓦斯等级等），我会结合案例库推荐合适的液压支架，并说明依据。',
      },
    ],
  }),
  actions: {
    pushUser(text) { this.messages.push({ role: 'user', text }) },
    pushAssistant(text) { this.messages.push({ role: 'assistant', text }) },
    pushCard(card) { this.messages.push({ role: 'assistant', card }) },
    setSession(id) { this.sessionId = id },
    clear() { this.messages = []; this.sessionId = null },
  },
})
