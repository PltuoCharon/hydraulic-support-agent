<template>
  <div class="engineering-empty">
    <div class="empty-symbol">
      +
    </div>

    <strong>
      {{ title }}
    </strong>

    <p>
      {{ description }}
    </p>

    <div
      v-if="$slots.default"
      class="empty-actions"
    >
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },

  description: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.engineering-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  min-height: 230px;

  padding: 30px 24px;

  text-align: center;
}

.empty-symbol {
  display: flex;
  align-items: center;
  justify-content: center;

  width: 42px;
  height: 42px;

  margin-bottom: 13px;

  color: var(--hs-blue-600);
  background: #edf5ff;

  border: 1px solid #cfe2f6;
  border-radius: 10px;

  font-size: 25px;
  font-weight: 300;
}

strong {
  color: var(--hs-gray-950);

  font-size: 14px;
}

p {
  max-width: 300px;

  margin: 7px 0 0;

  color: var(--hs-gray-500);

  font-size: 12px;
  line-height: 1.65;
}

.empty-actions {
  margin-top: 15px;
}
</style>
