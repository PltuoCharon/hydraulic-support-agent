// W30-D3: 可信度角标统一判定(疑/估/缺/实), 供 ResultView/WizardView 共用
// 口径: 判定读 support_status + support_source 原文; 前端 NULL 兜底文案不参与判定
export function badge(it) {
  if (it.support_status === 'suspect') return { text: '疑', type: 'danger' }
  const src = it.support_source || ''
  if (src.includes('估算')) return { text: '估', type: 'warning' }
  if (src.includes('未查到公开参数')) return { text: '缺', type: 'info' }
  return { text: '实', type: 'success' }
}
