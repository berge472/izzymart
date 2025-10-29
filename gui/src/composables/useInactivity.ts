import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Composable to track user inactivity
 * @param timeoutMs - Time in milliseconds before triggering inactivity callback
 * @param onInactive - Callback function when user becomes inactive
 */
export function useInactivity(timeoutMs: number, onInactive: () => void) {
  const isActive = ref(true)
  let timeoutId: number | null = null

  function resetTimer() {
    isActive.value = true

    if (timeoutId !== null) {
      clearTimeout(timeoutId)
    }

    timeoutId = window.setTimeout(() => {
      isActive.value = false
      onInactive()
    }, timeoutMs)
  }

  function handleActivity() {
    resetTimer()
  }

  function cleanup() {
    if (timeoutId !== null) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  onMounted(() => {
    // Track various user activity events
    const events = [
      'mousedown',
      'mousemove',
      'keypress',
      'scroll',
      'touchstart',
      'click'
    ]

    events.forEach(event => {
      window.addEventListener(event, handleActivity)
    })

    // Start the initial timer
    resetTimer()

    // Cleanup on unmount
    onUnmounted(() => {
      cleanup()
      events.forEach(event => {
        window.removeEventListener(event, handleActivity)
      })
    })
  })

  return {
    isActive,
    resetTimer,
    cleanup
  }
}
