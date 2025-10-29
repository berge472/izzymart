<template>
  <div v-if="isActive" class="screensaver" @click="deactivate" @touchstart="deactivate">
    <div
      class="bouncing-text"
      :style="{
        left: position.x + 'px',
        top: position.y + 'px'
      }"
    >
      {{ storeName }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useSettingsStore } from '@/store/settings'

export default {
  props: {
    modelValue: {
      type: Boolean,
      required: true
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const settingsStore = useSettingsStore()

    const isActive = ref(props.modelValue)
    const storeName = ref(settingsStore.storeName)

    // Position and velocity
    const position = ref({ x: 0, y: 0 })
    const velocity = ref({ x: 2, y: 2 })

    // Text dimensions (approximate)
    const textWidth = ref(0)
    const textHeight = ref(60)

    let animationFrame = null

    // Sync with parent
    watch(() => props.modelValue, (newValue) => {
      isActive.value = newValue
      if (newValue) {
        startAnimation()
      } else {
        stopAnimation()
      }
    })

    watch(isActive, (newValue) => {
      emit('update:modelValue', newValue)
    })

    // Watch for store name changes
    watch(() => settingsStore.storeName, (newName) => {
      storeName.value = newName
      calculateTextWidth()
    })

    function calculateTextWidth() {
      // Approximate text width based on characters (more accurate measurement would require canvas)
      // Average character width at 4rem font size is roughly 40px
      textWidth.value = storeName.value.length * 40
    }

    function startAnimation() {
      // Initialize position at random location
      const maxX = window.innerWidth - textWidth.value
      const maxY = window.innerHeight - textHeight.value

      position.value = {
        x: Math.random() * maxX,
        y: Math.random() * maxY
      }

      // Random initial velocity direction
      velocity.value = {
        x: (Math.random() > 0.5 ? 1 : -1) * 2,
        y: (Math.random() > 0.5 ? 1 : -1) * 2
      }

      calculateTextWidth()
      animate()
    }

    function animate() {
      const maxX = window.innerWidth - textWidth.value
      const maxY = window.innerHeight - textHeight.value

      // Update position
      position.value.x += velocity.value.x
      position.value.y += velocity.value.y

      // Bounce off edges
      if (position.value.x <= 0 || position.value.x >= maxX) {
        velocity.value.x *= -1
        // Clamp position to prevent getting stuck
        position.value.x = Math.max(0, Math.min(maxX, position.value.x))
      }

      if (position.value.y <= 0 || position.value.y >= maxY) {
        velocity.value.y *= -1
        // Clamp position to prevent getting stuck
        position.value.y = Math.max(0, Math.min(maxY, position.value.y))
      }

      animationFrame = requestAnimationFrame(animate)
    }

    function stopAnimation() {
      if (animationFrame !== null) {
        cancelAnimationFrame(animationFrame)
        animationFrame = null
      }
    }

    function deactivate() {
      isActive.value = false
      stopAnimation()
    }

    onMounted(() => {
      if (isActive.value) {
        startAnimation()
      }
    })

    onUnmounted(() => {
      stopAnimation()
    })

    return {
      isActive,
      storeName,
      position,
      deactivate
    }
  }
}
</script>

<style scoped>
.screensaver {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #000;
  z-index: 9999;
  cursor: pointer;
}

.bouncing-text {
  position: absolute;
  font-size: 4rem;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
  user-select: none;
  pointer-events: none;
}
</style>
