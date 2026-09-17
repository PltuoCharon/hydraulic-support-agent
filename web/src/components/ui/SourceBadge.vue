<template>
  <span
    class="source-badge"
    :class="`source-${type}`"
  >
    {{ text }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'unknown',
  },
})

const labels = {
  manufacturer: '厂家',
  paper: '论文',
  standard: '标准',
  calculated: '计算',
  estimated: '估算',
  missing: '缺失',
  unknown: '未知',
}

const text = computed(
  () => labels[props.type] || props.type
)
</script>

<style scoped>
.source-badge {
  display: inline-flex;

  padding: 3px 7px;

  border: 1px solid var(--hs-gray-300);
  border-radius: 5px;

  color: var(--hs-gray-600);
  background: #fff;

  font-size: 11px;
  font-weight: 600;
}

.source-standard,
.source-paper {
  color: #2867aa;
  border-color: #bdd7f5;
  background: #f2f7fd;
}

.source-manufacturer {
  color: #276a4a;
  border-color: #bee3d0;
  background: #f1faf5;
}

.source-calculated {
  color: #7253a5;
  border-color: #d6c9eb;
  background: #f8f5fc;
}

.source-estimated {
  color: #996813;
  border-color: #f1d69a;
  background: #fff9e9;
}

.source-missing {
  color: #78828e;
  background: #f4f5f6;
}
</style>
