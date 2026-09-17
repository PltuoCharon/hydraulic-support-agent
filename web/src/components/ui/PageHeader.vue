<template>
  <header class="page-header">
    <div>
      <div
        v-if="eyebrow"
        class="page-eyebrow"
      >
        {{ eyebrow }}
      </div>

      <h1>{{ title }}</h1>

      <p v-if="description">
        {{ description }}
      </p>
    </div>

    <div class="page-actions">
      <slot />
    </div>
  </header>
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
  eyebrow: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;

  margin-bottom: 20px;
}

.page-eyebrow {
  margin-bottom: 5px;

  color: var(--hs-blue-600);

  font-size: 12px;
  font-weight: 700;

  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  margin: 0;

  color: var(--hs-gray-950);

  font-size: 24px;
  line-height: 1.3;
  font-weight: 700;
}

p {
  max-width: 900px;

  margin: 7px 0 0;

  color: var(--hs-gray-600);

  font-size: 14px;
  line-height: 1.7;
}

.page-actions {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 8px;
}
</style>
