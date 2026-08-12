<script setup>
// props: 父组件传进来的数据（只读，子组件不许改）
defineProps({
  areas: { type: Array, required: true },
  show: { type: Boolean, default: true },
})

// emit: 子组件向父组件抛事件（数据变更请求）
const emit = defineEmits(['select'])

const pick = (area) => emit('select', area)
</script>

<template>
  <ul v-if="show">
    <li v-for="a in areas" :key="a.id" @click="pick(a)" class="row">
      {{ a.area_name }} —— 煤层 {{ a.coal_thickness }}m
    </li>
  </ul>
  <p v-else>列表已隐藏</p>
</template>

<style scoped>
.row { cursor: pointer; padding: 4px 0; }
.row:hover { color: #42b883; }
</style>
