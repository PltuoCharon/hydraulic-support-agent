<template>
  <div class="qneed-view">
    <el-alert type="warning" :closable="false" style="margin-bottom:12px">
      公式出处：纵帅等《大采高综采工作面液压支架选型研究及应用》谢桥矿实例；取三式最大值作为需求支护强度。
    </el-alert>
    <el-form label-width="180px" style="max-width:560px">
      <el-form-item label="采高 hm (m)"><el-input-number v-model="form.hm" :min="0.5" :max="10" :step="0.1" /></el-form-item>
      <el-form-item label="周期来压步距 L1 (m)"><el-input-number v-model="form.l1" :min="1" :max="60" :step="1" /></el-form-item>
      <el-form-item label="控顶距 Lp (m)"><el-input-number v-model="form.lp" :min="1" :max="20" :step="0.1" /></el-form-item>
      <el-form-item label="支架中心距 Bc (m)"><el-input-number v-model="form.bc" :min="0.5" :max="6" :step="0.05" /></el-form-item>
      <el-form-item label="动载系数 N"><el-input-number v-model="form.n" :min="1" :max="3" :step="0.01" /></el-form-item>
      <el-form-item>
        <el-button type="primary" @click="run">计算</el-button>
        <el-button @click="fillXieqiao">填入谢桥实例</el-button>
      </el-form-item>
    </el-form>
    <template v-if="res">
      <el-descriptions :column="3" border style="max-width:760px">
        <el-descriptions-item label="p1 岩重法">{{ res.p1_mpa }} MPa</el-descriptions-item>
        <el-descriptions-item label="p2 来压步距法">{{ res.p2_mpa }} MPa</el-descriptions-item>
        <el-descriptions-item label="p3 统计公式">{{ res.p3_mpa }} MPa</el-descriptions-item>
      </el-descriptions>
      <div class="verdict">
        需求支护强度 q_need = <b>{{ res.q_need_mpa }} MPa</b>
        <el-tag style="margin-left:8px">控制式：{{ res.governing }}</el-tag>
      </div>
      <div class="foot">
        <p>取值规则：{{ res.rule }}</p>
        <p>出处：{{ res.source }}</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { postQNeed } from '../api'

const form = reactive({ hm: 6.0, l1: 25, lp: 15, bc: 5, n: 1.33 })
const res = ref(null)

const run = async () => {
  try {
    res.value = await postQNeed({ ...form })
  } catch (e) { /* 拦截器已统一提示 */ }
}
const fillXieqiao = () => { Object.assign(form, { hm: 6.0, l1: 25, lp: 15, bc: 5, n: 1.33 }); run() }
</script>

<style scoped>
.verdict { margin: 16px 0 8px; font-size: 15px; }
.foot { color: #909399; font-size: 12px; }
</style>
