<template>
  <span class="formula-badge">
    <span>ƒ</span>
    {{ id }}
  </span>
</template>

<script setup>
defineProps({
  id: {
    type: String,
    required: true,
  },
})
</script>

<style scoped>
.formula-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;

  padding: 4px 8px;

  color: var(--hs-navy-900);
  background: #edf4fa;

  border: 1px solid #cbddea;
  border-radius: 6px;

  font-size: 11px;
  font-family: Consolas, Monaco, monospace;
  font-weight: 700;
}
</style>
