<template>
  <div class="calc-center">
    <el-container style="height: calc(100vh - 60px)">
      <el-aside width="220px">
        <el-menu :default-active="mod" @select="onSelect">
          <el-menu-item index="qneed">需求阻力估算</el-menu-item>
          <el-menu-item index="column" disabled>立柱缸径反算（W33-D3 待建）</el-menu-item>
          <el-menu-item index="jack" disabled>千斤顶校核（W34 待建）</el-menu-item>
          <el-menu-item index="valve" disabled>阀组选型（W35 待建）</el-menu-item>
          <el-menu-item index="pump" disabled>泵站匹配（W35 待建）</el-menu-item>
        </el-menu>
        <el-alert type="info" :closable="false" style="margin:12px">
          边界声明：本模块为参数化设计计算与校核，不生成结构设计图样。
        </el-alert>
      </el-aside>
      <el-main>
        <QNeedView v-if="mod === 'qneed'" />
        <el-empty v-else description="该子模块尚未建设" />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import QNeedView from './QNeedView.vue'

const route = useRoute()
const router = useRouter()
const mod = ref(route.query.m || 'qneed')

const onSelect = (m) => { mod.value = m; router.replace({ query: { ...route.query, m } }) }
watch(() => route.query.m, (m) => { if (m) mod.value = m })
</script>
