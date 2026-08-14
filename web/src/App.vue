<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const active = computed(() => route.path)
</script>
<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar-inner">
        <div class="brand">
          <div class="brand-logo">支</div>
          <div>
            <div class="brand-name">液压支架选型系统</div>
            <div class="brand-sub">HYDRAULIC SUPPORT SELECTION</div>
          </div>
        </div>
        <el-menu :default-active="active" mode="horizontal" router class="topmenu">
          <el-menu-item index="/input">工况输入</el-menu-item>
          <el-menu-item index="/areas">矿区选择</el-menu-item>
          <el-menu-item index="/result">推荐结果</el-menu-item>
          <el-menu-item index="/compare">对比分析</el-menu-item>
          <el-menu-item index="/modify">部件修改</el-menu-item>
          <el-menu-item index="/chat">智能体对话</el-menu-item>
        </el-menu>
      </div>
    </header>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>
<style>
/* ============ 全局主题（作用于所有页面） ============ */
:root {
  --brand-blue: #16324f;
  --brand-blue-2: #1f4a75;
  --brand-accent: #f0a94c;
  --page-bg: #f4f6fa;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--page-bg);
  color: #2b3a4a;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
}
.app-shell { min-height: 100vh; display: flex; flex-direction: column; }

/* —— 顶部栏 —— */
.topbar {
  background: linear-gradient(120deg, var(--brand-blue), var(--brand-blue-2));
  box-shadow: 0 2px 12px rgba(22, 50, 79, .25);
  position: sticky; top: 0; z-index: 20;
}
.topbar-inner {
  max-width: 1200px; margin: 0 auto; padding: 0 24px;
  display: flex; align-items: center; justify-content: space-between;
  height: 64px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-logo {
  width: 38px; height: 38px; border-radius: 10px;
  background: linear-gradient(135deg, var(--brand-accent), #ffc46b);
  color: var(--brand-blue); font-weight: 800; font-size: 20px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px rgba(240, 169, 76, .4);
}
.brand-name { color: #fff; font-size: 17px; font-weight: 600; letter-spacing: .5px; }
.brand-sub { color: #9fb6cf; font-size: 11px; letter-spacing: 1.5px; }

/* —— 导航 —— */
.topmenu {
  border-bottom: none !important;
  --el-menu-bg-color: transparent;
  --el-menu-hover-bg-color: rgba(255, 255, 255, .08);
  --el-menu-active-color: #fff;
}
.topmenu .el-menu-item { color: #c7d5e4; font-size: 14px; margin: 0 4px; }
.topmenu .el-menu-item:hover { color: #fff; }
.topmenu .el-menu-item.is-active { color: #fff; font-weight: 600; border-bottom-color: var(--brand-accent) !important; }

/* —— 内容区 —— */
.content { max-width: 1200px; margin: 0 auto; padding: 28px 24px 56px; width: 100%; }

/* —— 页面标题统一（色条装饰） —— */
.content h2 {
  position: relative; font-size: 21px; color: var(--brand-blue);
  margin: 0 0 20px; padding-left: 14px; font-weight: 700;
}
.content h2::before {
  content: ''; position: absolute; left: 0; top: 4px; bottom: 4px;
  width: 4px; border-radius: 2px; background: var(--brand-accent);
}

/* —— 卡片质感 —— */
.el-card {
  border-radius: 12px; border: none;
  box-shadow: 0 1px 4px rgba(22, 50, 79, .06);
  transition: box-shadow .2s ease, transform .2s ease;
}
.el-card:hover { box-shadow: 0 6px 20px rgba(22, 50, 79, .10); }

/* —— 表单/描述/表格圆角 —— */
.el-descriptions, .el-table { border-radius: 8px; overflow: hidden; }
.el-alert { border-radius: 8px; }
</style>
