<template>
  <v-app>
    <DebugIndicator />
    <router-view />
  </v-app>
</template>

<script setup lang="ts">
import { useSettingsStore } from '@/store/settings'
import DebugIndicator from '@/components/DebugIndicator.vue'

// Initialize settings store to apply theme on app load
const settingsStore = useSettingsStore()
</script>

<style>
:root {
  /* Default theme colors - will be overridden by settings store */
  --color-primary: #667eea;
  --color-secondary: #764ba2;
  --color-accent: #f093fb;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

/* Apply theme colors to Vuetify components */
.v-app-bar {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%) !important;
}

.v-btn.v-btn--variant-elevated.bg-primary,
.v-btn.v-btn--variant-flat.bg-primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%) !important;
}

.v-chip.bg-primary {
  background: var(--color-primary) !important;
}
</style>
