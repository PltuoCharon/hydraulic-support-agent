// W30-D3: 可信度角标统一判定(疑/估/缺/实); W30-D6: 补 tip 字段, ResultView 迁入共用
// 口径: 判定读 support_status + support_source 原文; 前端 NULL 兜底文案不参与判定
export function badge(it) {
  const s = it.support_source || ''
  if (it.support_status === 'suspect') return { text: '疑', type: 'danger', tip: s || '存疑数据' }
  if (s.includes('估算')) return { text: '估', type: 'warning', tip: s }
  if (s.includes('未查到公开参数')) return { text: '缺', type: 'info', tip: s }
  return { text: '实', type: 'success', tip: s || '实测/文献参数' }
}
