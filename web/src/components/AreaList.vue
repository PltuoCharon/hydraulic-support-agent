<script setup>
defineProps({
  areas: { type: Array, required: true },
  show: { type: Boolean, default: true },
})
const emit = defineEmits(['select'])
const pick = (row) => emit('select', row)
</script>

<template>
  <el-table v-if="show" :data="areas" @row-click="pick"
            style="max-width: 600px" stripe>
    <el-table-column prop="id" label="ID" width="60" />
    <el-table-column prop="area_name" label="矿区" />
    <el-table-column prop="coal_thickness" label="煤层厚度(m)" width="120" />
  </el-table>
  <el-empty v-else description="列表已隐藏" />
</template>
