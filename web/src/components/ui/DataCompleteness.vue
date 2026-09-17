<template>
  <div
    class="data-completeness"
    :class="{ compact }"
  >
    <div class="completeness-head">
      <span>{{ label }}</span>

      <strong>
        {{ filled }}/{{ total }}
        <small>{{ percent }}%</small>
      </strong>
    </div>

    <div class="track">
      <div
        class="bar"
        :class="tone"
        :style="{ width: `${percent}%` }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  filled: {
    type: Number,
    required: true,
  },

  total: {
    type: Number,
    required: true,
  },

  label: {
    type: String,
    default: '关键工况字段完整度',
  },

  compact: {
    type: Boolean,
    default: false,
  },
})


const percent = computed(() => {
  if (!props.total) return 0

  return Math.round(
    props.filled / props.total * 100
  )
})


const tone = computed(() => {
  if (percent.value >= 80) {
    return 'good'
  }

  if (percent.value >= 50) {
    return 'warning'
  }

  return 'low'
})
</script>

<style scoped>
.data-completeness {
  width: 100%;
}

.completeness-head {
  display: flex;
  align-items: center;
  justify-content: space-between;

  margin-bottom: 7px;

  color: var(--hs-gray-600);

  font-size: 12px;
}

.completeness-head strong {
  color: var(--hs-gray-800);

  font-size: 12px;
}

.completeness-head small {
  margin-left: 4px;

  color: var(--hs-gray-500);

  font-size: 10px;
  font-weight: 500;
}

.track {
  overflow: hidden;

  height: 6px;

  background: var(--hs-gray-100);

  border-radius: 999px;
}

.bar {
  height: 100%;

  border-radius: inherit;

  transition: width 180ms ease;
}

.bar.good {
  background: var(--hs-green-600);
}

.bar.warning {
  background: var(--hs-yellow-600);
}

.bar.low {
  background: var(--hs-red-600);
}

.compact .completeness-head {
  margin-bottom: 5px;

  font-size: 11px;
}

.compact .track {
  height: 5px;
}
</style>
