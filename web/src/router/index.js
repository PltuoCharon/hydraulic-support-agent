import {
  createRouter,
  createWebHashHistory,
} from 'vue-router'


const routes = [

  // W34-D4: 新工程工作台
  {
    path: '/',
    redirect: '/workbench',
  },

  {
    path: '/workbench',
    name: 'workbench',
    component: () =>
      import('../views/WorkbenchView.vue'),
    meta: {
      title: '工程工作台',
    },
  },


  // ==========================================================
  // 智能选型
  // ==========================================================

  {
    path: '/select',
    name: 'select',
    component: () =>
      import('../views/SelectCenterView.vue'),
    meta: {
      title: '智能选型',
    },
  },

  {
    path: '/input',
    redirect: '/select?tab=form',
  },

  {
    path: '/wizard',
    redirect: '/select?tab=wizard',
  },

  {
    path: '/chat',
    redirect: '/select?tab=chat',
  },

  {
    path: '/result',
    name: 'result',
    component: () =>
      import('../views/ResultView.vue'),
    meta: {
      title: '推荐结果',
    },
  },

  {
    path: '/compare',
    name: 'compare',
    component: () =>
      import('../views/CompareView.vue'),
    meta: {
      title: '支架对比',
    },
  },


  // ==========================================================
  // 支架数据库
  // ==========================================================

  {
    path: '/areas',
    name: 'areas',
    component: () =>
      import('../views/AreasView.vue'),
    meta: {
      title: '矿区工况',
    },
  },

  {
    path: '/map',
    name: 'map',
    component: () =>
      import('../views/MapView.vue'),
    meta: {
      title: '矿区地图',
    },
  },

  {
    path: '/spectrum',
    name: 'spectrum',
    component: () =>
      import('../views/SpectrumView.vue'),
    meta: {
      title: '架型谱系',
    },
  },

  {
    path: '/vendors',
    name: 'vendors',
    component: () =>
      import('../views/VendorView.vue'),
    meta: {
      title: '制造商',
    },
  },

  {
    path: '/data-quality',
    name: 'data-quality',
    component: () =>
      import('../views/DataQualityView.vue'),
    meta: {
      title: '数据质量',
    },
  },


  // ==========================================================
  // 设计计算
  // ==========================================================

  {
    path: '/calc',
    name: 'calc',
    component: () =>
      import('../views/CalcCenterView.vue'),
    meta: {
      title: '设计计算',
    },
  },


  // legacy route：W34 Formula Registry 已标记
  {
    path: '/modify',
    name: 'modify',
    component: () =>
      import('../views/ModifyView.vue'),
    meta: {
      title: '历史部件修改',
      legacy: true,
    },
  },
]


const router = createRouter({
  history: createWebHashHistory(),
  routes,
})


export default router
