<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const active = computed(() => route.path)
</script>

<template>
  <div class="layout">
    <h1>液压支架选型系统</h1>
    <el-menu :default-active="active" mode="horizontal" router>
      <el-menu-item index="/input">工况输入</el-menu-item>
      <el-menu-item index="/areas">矿区选择</el-menu-item>
      <el-menu-item index="/result">推荐结果</el-menu-item>
      <el-menu-item index="/chat">智能体对话</el-menu-item>
    </el-menu>
    <main class="page">
      <router-view />
    </main>
  </div>
</template>

<style>
.layout { max-width: 960px; margin: 0 auto; padding: 16px; }
.page { margin-top: 16px; }
</style>
