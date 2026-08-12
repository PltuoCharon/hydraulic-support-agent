import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/input' },
  { path: '/input', name: 'input', component: () => import('../views/InputView.vue'),
    meta: { title: '工况输入' } },
  { path: '/areas', name: 'areas', component: () => import('../views/AreasView.vue'),
    meta: { title: '矿区选择' } },
  { path: '/result', name: 'result', component: () => import('../views/ResultView.vue'),
    meta: { title: '推荐结果' } },
]

export default createRouter({
  history: createWebHashHistory(),   // hash 模式: 静态部署刷新不 404
  routes,
})
