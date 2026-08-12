import { defineStore } from 'pinia'

// 匹配 store: 工况条件 + 匹配结果, 跨路由共享
export const useMatchStore = defineStore('match', {
  state: () => ({
    conditions: null,   // 提交的工况参数
    result: null,       // /api/match 返回 {total, items}
    fromArea: null,     // 来源矿区(矿区路径选中时记录, D5 用)
  }),
  actions: {
    // 矿区路径: 选中矿区的工况字段 → 预填表单
    prefillFromArea(area) {
      this.fromArea = { id: area.id, area_name: area.area_name }
      this.conditions = {
        coal_thickness: area.coal_thickness,
        dip_angle: area.dip_angle,
        mining_height_min: area.mining_height_min,
        mining_height_max: area.mining_height_max,
        hardness_f: area.hardness_f,
        roof_category: area.roof_category || '',
        floor_pressure: area.floor_pressure ? Number(area.floor_pressure) : null,
        mine_pressure: area.mine_pressure || '',
        gas_level: area.gas_level || '',
        depth: area.depth,
        face_length: area.face_length,
      }
    },
    setResult(conditions, result) {
      this.conditions = conditions
      this.result = result
    },
  },
})
