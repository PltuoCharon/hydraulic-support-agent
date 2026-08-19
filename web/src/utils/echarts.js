import * as echarts from 'echarts/core'
import { RadarChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent,
         GridComponent, MarkLineComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
echarts.use([RadarChart, BarChart, TitleComponent, TooltipComponent,
             LegendComponent, GridComponent, MarkLineComponent,
             DataZoomComponent, CanvasRenderer])
// 品牌色板（藏青主色 + 金橙点缀，工业风格统一）
export const BRAND_COLORS = ['#1f4a75', '#f0a94c', '#3d8c9e', '#7a9bb5', '#c4d6e8']

export default echarts
