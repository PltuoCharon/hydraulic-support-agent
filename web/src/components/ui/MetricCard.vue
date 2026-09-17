<template>
  <div class="metric-card">
    <div class="metric-top">
      <span class="metric-label">
        {{ label }}
      </span>

      <span
        v-if="status"
        class="metric-status"
        :class="`is-${status}`"
      />
    </div>

    <div class="metric-value">
      {{ value ?? '—' }}
      <small v-if="unit">
        {{ unit }}
      </small>
    </div>

    <div
      v-if="note"
      class="metric-note"
    >
      {{ note }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    default: null,
  },
  unit: {
    type: String,
    default: '',
  },
  note: {
    type: String,
    default: '',
  },
  status: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.metric-card {
  min-height: 116px;

  padding: 17px 18px;

  background: #fff;

  border: 1px solid var(--hs-gray-200);
  border-radius: var(--hs-radius-lg);
}

.metric-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metric-label {
  color: var(--hs-gray-600);
  font-size: 13px;
}

.metric-status {
  width: 8px;
  height: 8px;

  border-radius: 50%;

  background: var(--hs-gray-300);
}

.metric-status.is-success {
  background: var(--hs-green-600);
}

.metric-status.is-warning {
  background: var(--hs-yellow-600);
}

.metric-status.is-danger {
  background: var(--hs-red-600);
}

.metric-value {
  margin-top: 9px;

  color: var(--hs-navy-900);

  font-size: 29px;
  font-weight: 720;
  line-height: 1.2;
}

.metric-value small {
  margin-left: 4px;

  color: var(--hs-gray-600);

  font-size: 13px;
  font-weight: 500;
}

.metric-note {
  margin-top: 8px;

  color: var(--hs-gray-500);

  font-size: 12px;
}
</style>
