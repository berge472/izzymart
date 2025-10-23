<template>
  <div class="scanner-input-handler">
    <!-- Hidden component - handles keyboard input for barcode scanner -->
    <v-snackbar
      v-model="showNotification"
      :color="notificationType"
      :timeout="3000"
      location="top"
    >
      <div class="d-flex align-center">
        <v-icon start>{{ notificationIcon }}</v-icon>
        <span>{{ notificationMessage }}</span>
      </div>
    </v-snackbar>

    <v-overlay
      v-model="isScanning"
      class="align-center justify-center"
      persistent
    >
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
      ></v-progress-circular>
      <p class="mt-4 text-h6">Scanning...</p>
    </v-overlay>

    <!-- Always-On Camera Scanner Preview -->
    <div
      v-if="settingsStore.cameraScanningEnabled"
      class="camera-scanner-preview"
    >
      <div id="camera-scanner-container"></div>
      <div class="scanner-status">
        <v-icon size="small" color="white">mdi-barcode-scan</v-icon>
        <span class="scanner-label">Scan Barcode</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, defineProps, defineEmits } from 'vue'
import { useCartStore } from '@/store/cart'
import { useSettingsStore } from '@/store/settings'
import { api } from '@/services/api'
import { Html5Qrcode } from 'html5-qrcode'
import { isDebugMode } from '@/utils/urlParams'

// Props to control behavior
const props = defineProps<{
  adminMode?: boolean  // If true, emit event instead of adding to cart
}>()

// Emit scanned UPC for admin mode
const emit = defineEmits<{
  'product-scanned': [upc: string]
}>()

const cartStore = useCartStore()
const settingsStore = useSettingsStore()

const scanBuffer = ref('')
const scanTimeout = ref<number | null>(null)
const isScanning = ref(false)
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref<'success' | 'error' | 'info'>('success')
const notificationIcon = ref('mdi-check-circle')

const SCAN_TIMEOUT_MS = 100 // Time between key presses to consider it a barcode scan
const MIN_BARCODE_LENGTH = 8 // Minimum length for a UPC code

// Camera scanner state
let html5QrCode: Html5Qrcode | null = null
const cameraInitialized = ref(false)

function handleKeyPress(event: KeyboardEvent) {
  // Ignore if user is typing in an input field
  const target = event.target as HTMLElement
  if (
    target.tagName === 'INPUT' ||
    target.tagName === 'TEXTAREA' ||
    target.isContentEditable
  ) {
    return
  }

  // Only handle number keys (barcode scanners typically send numbers)
  if (event.key >= '0' && event.key <= '9') {
    event.preventDefault()

    // Add to buffer
    scanBuffer.value += event.key

    // Clear existing timeout
    if (scanTimeout.value) {
      clearTimeout(scanTimeout.value)
    }

    // Set new timeout
    scanTimeout.value = window.setTimeout(() => {
      if (scanBuffer.value.length >= MIN_BARCODE_LENGTH) {
        processBarcode(scanBuffer.value)
      }
      scanBuffer.value = ''
    }, SCAN_TIMEOUT_MS)
  } else if (event.key === 'Enter' && scanBuffer.value.length > 0) {
    // Some scanners send Enter at the end
    event.preventDefault()

    if (scanTimeout.value) {
      clearTimeout(scanTimeout.value)
    }

    if (scanBuffer.value.length >= MIN_BARCODE_LENGTH) {
      processBarcode(scanBuffer.value)
    }

    scanBuffer.value = ''
  }
}

async function processBarcode(upc: string) {
  console.log('Processing barcode:', upc)

  // Play beep sound immediately before any API calls
  playBeep()

  // In admin mode, just emit the UPC and let parent handle it
  if (props.adminMode) {
    emit('product-scanned', upc)
    return
  }

  // Normal mode: add to cart
  isScanning.value = true

  try {
    // Use cache=false when debug mode is enabled via URL parameter
    const useCache = !isDebugMode()
    console.log(`Fetching product with cache=${useCache} (debug mode: ${isDebugMode()})`)
    const product = await api.getProductByUPC(upc, useCache)

    // Add to cart
    cartStore.addItem(product)
  } catch (error: any) {
    console.error('Error scanning product:', error)

    let errorMessage = 'Product not found'
    if (error.response?.status === 404) {
      errorMessage = `No product found for UPC: ${upc}`
    } else if (error.message) {
      errorMessage = error.message
    }

    // Play error sound
    playErrorSound()
    showError(errorMessage)
  } finally {
    isScanning.value = false
  }
}

function showSuccess(message: string) {
  notificationMessage.value = message
  notificationType.value = 'success'
  notificationIcon.value = 'mdi-check-circle'
  showNotification.value = true
}

function showError(message: string) {
  notificationMessage.value = message
  notificationType.value = 'error'
  notificationIcon.value = 'mdi-alert-circle'
  showNotification.value = true
}

function playBeep() {
  // Play the scanner beep MP3 file
  const audio = new Audio('/store-scanner-beep-sound-effect.mp3')
  audio.volume = 0.5
  audio.play().catch(error => {
    console.error('Error playing scanner beep sound:', error)
  })
}

function playErrorSound() {
  // Play the error sound MP3 file
  const audio = new Audio('/error-404.mp3')
  audio.volume = 0.5
  audio.play().catch(error => {
    console.error('Error playing error sound:', error)
  })
}

// Camera Scanner Functions
async function startCameraScanner() {
  if (cameraInitialized.value || !settingsStore.cameraScanningEnabled) {
    console.log('Camera scanner not starting:', {
      initialized: cameraInitialized.value,
      enabled: settingsStore.cameraScanningEnabled
    })
    return
  }

  console.log('Starting camera scanner...')

  // Wait for the container to be in the DOM
  await new Promise(resolve => setTimeout(resolve, 500))

  const container = document.getElementById('camera-scanner-container')
  if (!container) {
    console.error('Camera container not found')
    return
  }

  try {
    html5QrCode = new Html5Qrcode('camera-scanner-container')
    console.log('Html5Qrcode instance created')

    // More permissive config for better barcode detection
    const config = {
      fps: 10,
      qrbox: function(viewfinderWidth: number, viewfinderHeight: number) {
        // Square QR box, 70% of the smaller dimension
        const minEdge = Math.min(viewfinderWidth, viewfinderHeight)
        const qrboxSize = Math.floor(minEdge * 0.7)
        return {
          width: qrboxSize,
          height: qrboxSize
        }
      },
      aspectRatio: 1.0,
      disableFlip: false,
      // Try with explicit formats
      supportedScanTypes: [
        (window as any).Html5QrcodeScanType?.SCAN_TYPE_CAMERA
      ]
    }

    console.log('Starting camera with config:', config)

    await html5QrCode.start(
      { facingMode: 'environment' }, // Use back camera on mobile
      config,
      (decodedText, decodedResult) => {
        // Successfully scanned a barcode
        console.log('✅ BARCODE DETECTED!', {
          text: decodedText,
          format: decodedResult.result.format,
          result: decodedResult
        })
        processBarcode(decodedText)
      },
      (errorMessage) => {
        // Log errors occasionally for debugging (every 50th error)
        if (Math.random() < 0.02) {
          console.log('Scanner error (sampled):', errorMessage)
        }
      }
    )

    console.log('✅ Camera scanner started successfully')
    cameraInitialized.value = true
  } catch (error) {
    console.error('❌ Error starting camera scanner:', error)
    showError('Could not access camera. Please check permissions.')
  }
}

async function stopCameraScanner() {
  if (html5QrCode && cameraInitialized.value) {
    try {
      await html5QrCode.stop()
      html5QrCode.clear()
    } catch (error) {
      console.error('Error stopping camera scanner:', error)
    }
    html5QrCode = null
    cameraInitialized.value = false
  }
}

// Watch for camera scanning setting changes
watch(() => settingsStore.cameraScanningEnabled, (enabled) => {
  if (enabled) {
    startCameraScanner()
  } else {
    stopCameraScanner()
  }
})

onMounted(() => {
  window.addEventListener('keydown', handleKeyPress)

  // Start camera if enabled
  if (settingsStore.cameraScanningEnabled) {
    startCameraScanner()
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
  if (scanTimeout.value) {
    clearTimeout(scanTimeout.value)
  }
  // Clean up camera scanner if still running
  stopCameraScanner()
})
</script>

<style scoped>
.scanner-input-handler {
  /* This component has no visual elements, only handles keyboard input */
}

.camera-scanner-preview {
  position: fixed;
  bottom: 20px;
  left: 20px;
  width: 300px;
  height: 300px;
  z-index: 50;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  background: #000;
  border: 3px solid var(--color-primary);
}

#camera-scanner-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.scanner-status {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 4px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 10;
}

.scanner-label {
  color: white;
  font-size: 11px;
  font-weight: 600;
}

/* Style the html5-qrcode elements */
:deep(#camera-scanner-container video) {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover;
}

/* Show the scanning box overlay */
:deep(#camera-scanner-container canvas) {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
}
</style>
