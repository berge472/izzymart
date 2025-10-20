<template>
  <div class="keyboard">
    <!-- Letter Rows -->
    <div class="keyboard-row" v-for="(row, rowIndex) in layout" :key="rowIndex">
      <v-btn
        v-for="key in row"
        :key="key"
        :class="['keyboard-key', getKeyClass(key)]"
        :size="getKeySize(key)"
        @click="handleKeyPress(key)"
        elevation="2"
      >
        <span v-if="key === 'backspace'">
          <v-icon>mdi-backspace</v-icon>
        </span>
        <span v-else-if="key === 'space'">Space</span>
        <span v-else-if="key === 'search'">
          <v-icon>mdi-magnify</v-icon>
          Search
        </span>
        <span v-else>{{ isShifted ? key.toUpperCase() : key }}</span>
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'search'): void
}>()

const isShifted = ref(false)

const layout = [
  ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
  ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
  ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
  ['shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', 'backspace'],
  ['space', 'search']
]

function handleKeyPress(key: string) {
  const currentValue = props.modelValue

  switch (key) {
    case 'backspace':
      emit('update:modelValue', currentValue.slice(0, -1))
      break

    case 'space':
      emit('update:modelValue', currentValue + ' ')
      break

    case 'shift':
      isShifted.value = !isShifted.value
      break

    case 'search':
      emit('search')
      break

    default: {
      const char = isShifted.value ? key.toUpperCase() : key
      emit('update:modelValue', currentValue + char)

      // Auto-reset shift after typing a character
      if (isShifted.value && key !== 'shift') {
        isShifted.value = false
      }
      break
    }
  }
}

function getKeyClass(key: string): string {
  const classes = []

  if (key === 'shift' && isShifted.value) {
    classes.push('active')
  }

  if (['shift', 'backspace', 'space', 'search'].includes(key)) {
    classes.push('special-key')
  }

  if (key === 'search') {
    classes.push('search-key')
  }

  return classes.join(' ')
}

function getKeySize(key: string): string {
  if (key === 'space') return 'x-large'
  if (key === 'search') return 'x-large'
  if (key === 'backspace' || key === 'shift') return 'large'
  return 'large'
}
</script>

<style scoped>
.keyboard {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background-color: #e0e0e0;
  border-radius: 12px;
}

.keyboard-row {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.keyboard-key {
  min-width: 60px !important;
  min-height: 60px !important;
  font-size: 1.2rem !important;
  font-weight: 600 !important;
  text-transform: none !important;
  background-color: #ffffff !important;
  color: #1a1a1a !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
}

.keyboard-key:active {
  transform: scale(0.95);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

.keyboard-key.special-key {
  background-color: #e3f2fd !important;
  color: #1976d2 !important;
}

.keyboard-key.special-key.active {
  background-color: #1976d2 !important;
  color: #ffffff !important;
}

.keyboard-key.search-key {
  background: linear-gradient(135deg, #43a047 0%, #2e7d32 100%) !important;
  color: #ffffff !important;
  flex: 1;
  font-size: 1.3rem !important;
}

.keyboard-key:nth-last-child(1):nth-child(1) {
  /* Space key - make it wider */
  flex: 2;
}

.keyboard-row:last-child {
  gap: 12px;
}

.keyboard-row:last-child .keyboard-key:first-child {
  /* Space key */
  flex: 3;
}

.keyboard-row:last-child .keyboard-key:last-child {
  /* Search key */
  flex: 2;
}
</style>
