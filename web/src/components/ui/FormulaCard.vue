<template>
  <section class="formula-card">
    <div class="formula-head">
      <div>
        <div
          v-if="eyebrow"
          class="formula-eyebrow"
        >
          {{ eyebrow }}
        </div>

        <h4>{{ title }}</h4>
      </div>

      <span
        v-if="formulaId"
        class="formula-id"
      >
        {{ formulaId }}
      </span>
    </div>

    <div
      v-if="formula"
      class="formula-expression"
    >
      {{ formula }}
    </div>

    <p
      v-if="description"
      class="formula-description"
    >
      {{ description }}
    </p>

    <div
      v-if="$slots.default"
      class="formula-body"
    >
      <slot />
    </div>

    <div
      v-if="source || $slots.source"
      class="formula-source"
    >
      <span>依据</span>

      <div>
        <slot name="source">
          {{ source }}
        </slot>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  eyebrow: {
    type: String,
    default: 'Formula',
  },

  title: {
    type: String,
    required: true,
  },

  formulaId: {
    type: String,
    default: '',
  },

  formula: {
    type: String,
    default: '',
  },

  description: {
    type: String,
    default: '',
  },

  source: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.formula-card {
  padding: 18px 20px;
  background: #f8fafc;
  border: 1px solid #dfe6ee;
  border-left: 3px solid #2f80ed;
  border-radius: 8px;
}

.formula-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.formula-eyebrow {
  margin-bottom: 4px;
  color: #2f80ed;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.formula-head h4 {
  margin: 0;
  color: #17324d;
  font-size: 15px;
}

.formula-id {
  flex: none;
  padding: 4px 8px;
  color: #46637f;
  background: #eef3f8;
  border-radius: 5px;
  font-family: Consolas, Monaco, monospace;
  font-size: 11px;
}

.formula-expression {
  margin-top: 14px;
  padding: 11px 14px;
  color: #123b61;
  background: #fff;
  border: 1px solid #e3e9ef;
  border-radius: 6px;
  font-family:
    "Times New Roman",
    "STIX Two Math",
    serif;
  font-size: 17px;
}

.formula-description {
  margin: 10px 0 0;
  color: #667085;
  font-size: 13px;
  line-height: 1.65;
}

.formula-body {
  margin-top: 12px;
}

.formula-source {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr);
  gap: 10px;
  margin-top: 13px;
  padding-top: 11px;
  border-top: 1px solid #e3e9ef;
  color: #667085;
  font-size: 12px;
  line-height: 1.6;
}

.formula-source > span {
  color: #8a94a3;
}
</style>
