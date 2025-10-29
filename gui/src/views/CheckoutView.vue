<template>
  <v-container fluid class="checkout-container pa-0">
    <v-row no-gutters class="fill-height">
      <!-- Left side: Item Details (2/3 width) -->
      <v-col cols="8" class="details-section">
        <ItemDetails />
      </v-col>

      <!-- Right side: Cart (1/3 width) -->
      <v-col cols="4" class="cart-section">
        <CartList />
      </v-col>
    </v-row>

    <!-- Search Dialog with Keyboard -->
    <SearchDialog v-model="showSearch" />

    <!-- Scanner Input Handler -->
    <ScannerInput @barcode-detected="handleBarcodeDetected" />

    <!-- Screensaver -->
    <Screensaver v-model="showScreensaver" />
  </v-container>
</template>

<script>
import { ref, provide, watch, onMounted } from 'vue'
import ItemDetails from '@/components/ItemDetails.vue'
import CartList from '@/components/CartList.vue'
import SearchDialog from '@/components/SearchDialog.vue'
import ScannerInput from '@/components/ScannerInput.vue'
import Screensaver from '@/components/Screensaver.vue'
import { useInactivity } from '@/composables/useInactivity'
import { useCartStore } from '@/store/cart'
import { getUrlParam } from '@/utils/urlParams'
import { api } from '@/services/api'

export default {
  components: {
    ItemDetails,
    CartList,
    SearchDialog,
    ScannerInput,
    Screensaver
  },
  setup() {
    const showSearch = ref(false)
    const showScreensaver = ref(false)
    const cartStore = useCartStore()

    // Provide search dialog toggle for child components
    provide('toggleSearch', () => {
      showSearch.value = !showSearch.value
    })

    // Track user inactivity - trigger screensaver after 5 minutes (300000ms)
    const { resetTimer } = useInactivity(300000, () => {
      // Only activate screensaver if no dialogs are open
      if (!showSearch.value) {
        showScreensaver.value = true
      }
    })

    // Reset inactivity timer when dialogs open/close
    watch(showSearch, (isOpen) => {
      if (!isOpen) {
        resetTimer()
      }
    })

    // Reset inactivity timer when screensaver closes
    watch(showScreensaver, (isActive) => {
      if (!isActive) {
        resetTimer()
      }
    })

    // Watch for product scans - dismiss screensaver and reset timer
    watch(() => cartStore.lastScannedItem, (newItem) => {
      if (newItem) {
        // Dismiss screensaver if active
        if (showScreensaver.value) {
          showScreensaver.value = false
        }
        // Reset the inactivity timer
        resetTimer()
      }
    })

    // Function to manually activate screensaver (for settings button)
    function activateScreensaver() {
      showScreensaver.value = true
    }

    // Provide screensaver activation for child components
    provide('activateScreensaver', activateScreensaver)

    // Handle barcode detection - close all dialogs
    function handleBarcodeDetected() {
      // Close search dialog if open
      if (showSearch.value) {
        showSearch.value = false
      }
      // Screensaver will auto-close via the cart store watcher
    }

    // Check for UPC parameter on mount (for testing)
    onMounted(async () => {
      const upc = getUrlParam('upc')
      if (upc) {
        try {
          console.log(`Loading product from URL parameter: ${upc}`)
          const product = await api.getProductByUPC(upc)
          cartStore.addItem(product)
        } catch (error) {
          console.error('Error loading product from UPC parameter:', error)
        }
      }
    })

    return {
      showSearch,
      showScreensaver,
      handleBarcodeDetected
    }
  }
}
</script>

<style scoped>
.checkout-container {
  height: 100vh;
  width: 100vw;
  background-color: #f5f5f5;
}

.details-section {
  background-color: #ffffff;
  border-right: 2px solid #e0e0e0;
  height: 100vh;
  overflow-y: auto;
}

.cart-section {
  background-color: #fafafa;
  height: 100vh;
  overflow-y: auto;
}
</style>
