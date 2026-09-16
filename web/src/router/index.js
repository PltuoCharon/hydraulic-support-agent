import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/select' },
  { path: '/select', name: 'select', component: () => import('../views/SelectCenterView.vue'), meta: { title: '选型中心' } },
  { path: '/input', redirect: '/select?tab=form' },
  { path: '/areas', name: 'areas', component: () => import('../views/AreasView.vue'), meta: { title: '矿区选择' } },
  { path: '/map', name: 'map', component: () => import('../views/MapView.vue'), meta: { title: '地图选区' } },
  { path: '/spectrum', name: 'spectrum', component: () => import('../views/SpectrumView.vue'), meta: { title: '架型谱系' } },
  { path: '/vendors', name: 'vendors', component: () => import('../views/VendorView.vue'), meta: { title: '厂商分布' } },
  { path: '/wizard', redirect: '/select?tab=wizard' },
  { path: '/result', name: 'result', component: () => import('../views/ResultView.vue'), meta: { title: '推荐结果' } },
  { path: '/compare', name: 'compare', component: () => import('../views/CompareView.vue'), meta: { title: '支架对比' } },
  { path: '/modify', name: 'modify', component: () => import('../views/ModifyView.vue'), meta: { title: '部件修改' } },
  { path: '/calc', name: 'calc', component: () => import('../views/CalcCenterView.vue'), meta: { title: '设计计算' } },
  { path: '/chat', redirect: '/select?tab=chat' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
