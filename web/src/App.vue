<script setup>
import { ref, reactive } from 'vue'
import AreaList from './components/AreaList.vue'

const title = ref('液压支架选型系统')
const showList = ref(true)
const selected = ref(null)   // 子组件点上来的矿区

const state = reactive({
  areas: [
    { id: 1, area_name: '兴隆庄4301', coal_thickness: 9.4 },
    { id: 2, area_name: '鲍店1316', coal_thickness: 6.0 },
    { id: 3, area_name: '寺河矿', coal_thickness: 6.2 },
  ]
})

const toggle = () => { showList.value = !showList.value }
const onSelect = (area) => { selected.value = area }
</script>

<template>
  <h1>{{ title }}</h1>
  <p>矿区数量：{{ state.areas.length }}</p>

  <el-button type="primary" @click="toggle">
    {{ showList ? '隐藏' : '显示' }}列表
  </el-button>

  <!-- props 传入 + emit 监听 -->
  <AreaList :areas="state.areas" :show="showList" @select="onSelect" />

  <p v-if="selected">
    已选中：<b>{{ selected.area_name }}</b>（煤层 {{ selected.coal_thickness }}m）
  </p>
</template>
