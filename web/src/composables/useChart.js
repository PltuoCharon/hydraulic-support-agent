import { onMounted, onBeforeUnmount, ref } from 'vue'
import echarts from '../utils/echarts'

export function useChart(elRef) {
  const chart = ref(null)
  let ro = null
  let timer = null

  onMounted(() => {
    chart.value = echarts.init(elRef.value)
    ro = new ResizeObserver(() => {
      clearTimeout(timer)
      timer = setTimeout(() => chart.value && chart.value.resize(), 80)
    })
    ro.observe(elRef.value)
  })

  const setOption = (opt) => chart.value && chart.value.setOption(opt, true)
  const resize = () => chart.value && chart.value.resize()

  onBeforeUnmount(() => {
    if (ro) ro.disconnect()
    if (chart.value) { chart.value.dispose(); chart.value = null }
  })

  return { chart, setOption, resize }
}
