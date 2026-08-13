import * as echarts from 'echarts/core'
import { RadarChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent,
         GridComponent, MarkLineComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
echarts.use([RadarChart, BarChart, TitleComponent, TooltipComponent,
             LegendComponent, GridComponent, MarkLineComponent,
             DataZoomComponent, CanvasRenderer])
export default echarts
