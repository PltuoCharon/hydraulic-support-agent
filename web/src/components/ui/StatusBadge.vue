<template>
  <span
    class="status-badge"
    :class="`is-${status}`"
  >
    <span class="dot" />
    {{ label }}
  </span>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  status: {
    type: String,
    default: 'neutral',
  },
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;

  padding: 4px 8px;

  color: var(--hs-gray-700);
  background: var(--hs-gray-100);

  border-radius: 999px;

  font-size: 12px;
  font-weight: 600;
}

.dot {
  width: 6px;
  height: 6px;

  border-radius: 50%;

  background: var(--hs-gray-500);
}

.is-success {
  color: #237a50;
  background: #eaf7f0;
}

.is-success .dot {
  background: var(--hs-green-600);
}

.is-warning {
  color: #996813;
  background: #fff6df;
}

.is-warning .dot {
  background: var(--hs-yellow-600);
}

.is-danger {
  color: #a73939;
  background: #fdecec;
}

.is-danger .dot {
  background: var(--hs-red-600);
}

.is-info {
  color: #2867aa;
  background: #ebf4ff;
}

.is-info .dot {
  background: var(--hs-blue-600);
}
</style>
