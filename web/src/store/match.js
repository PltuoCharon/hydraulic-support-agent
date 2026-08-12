import { defineStore } from 'pinia'

// 匹配 store: 工况条件 + 匹配结果, 跨路由共享
export const useMatchStore = defineStore('match', {
  state: () => ({
    conditions: null,   // 提交的工况参数
    result: null,       // /api/match 返回 {total, items}
    fromArea: null,     // 来源矿区(矿区路径选中时记录, D5 用)
  }),
  actions: {
    setResult(conditions, result) {
      this.conditions = conditions
      this.result = result
    },
  },
})
