import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/input' },
  { path: '/input', name: 'input', component: () => import('../views/InputView.vue'), meta: { title: '工况输入' } },
  { path: '/areas', name: 'areas', component: () => import('../views/AreasView.vue'), meta: { title: '矿区选择' } },
  { path: '/result', name: 'result', component: () => import('../views/ResultView.vue'), meta: { title: '推荐结果' } },
  { path: '/compare', name: 'compare', component: () => import('../views/CompareView.vue'), meta: { title: '支架对比' } },
  { path: '/modify', name: 'modify', component: () => import('../views/ModifyView.vue'), meta: { title: '部件修改' } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
