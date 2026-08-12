<script setup>
import { ref, reactive } from 'vue'

// 1. ref: 基本类型响应式
const title = ref('液压支架选型系统')
const showList = ref(true)

// 2. reactive: 对象响应式（先写死假数据，D6 换成真接口）
const state = reactive({
  areas: [
    { id: 1, area_name: '兴隆庄4301', coal_thickness: 9.4 },
    { id: 2, area_name: '鲍店1316', coal_thickness: 6.0 },
    { id: 3, area_name: '寺河矿', coal_thickness: 6.2 },
  ]
})

const toggle = () => { showList.value = !showList.value }
</script>

<template>
  <!-- 3. 模板插值 {{ }} -->
  <h1>{{ title }}</h1>
  <p>矿区数量：{{ state.areas.length }}</p>

  <!-- 4. 事件绑定 @click -->
  <button @click="toggle">{{ showList ? '隐藏' : '显示' }}列表</button>

  <!-- 5. v-if 条件渲染 + v-for 列表渲染 -->
  <ul v-if="showList">
    <li v-for="a in state.areas" :key="a.id">
      {{ a.area_name }} —— 煤层 {{ a.coal_thickness }}m
    </li>
  </ul>
  <p v-else>列表已隐藏</p>
</template>
