<template>
  <div v-if="isDebug" class="debug-indicator">
    <v-chip
      color="warning"
      size="small"
      prepend-icon="mdi-bug"
    >
      DEBUG MODE - Cache Disabled
    </v-chip>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { isDebugMode } from '@/utils/urlParams'

const isDebug = ref(false)

onMounted(() => {
  isDebug.value = isDebugMode()
  if (isDebug.value) {
    console.log('🐛 Debug mode is ENABLED - API caching is disabled')
  }
})
</script>

<style scoped>
.debug-indicator {
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 9999;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}
</style>
