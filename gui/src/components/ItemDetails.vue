<template>
  <div class="item-details-container">
    <!-- Settings Panel -->
    <SettingsPanel v-model="showSettings" />

    <!-- Header -->
    <v-app-bar color="primary" dark elevation="2">
      <v-btn
        icon="mdi-storefront"
        @click="showSettings = true"
        size="large"
      ></v-btn>
      <v-app-bar-title>
        {{ settingsStore.storeName }}
      </v-app-bar-title>
      <v-spacer></v-spacer>
      <v-chip color="white" text-color="primary" class="mr-4">
        <v-icon start>mdi-cart</v-icon>
        {{ cartStore.itemCount }} items
      </v-chip>
    </v-app-bar>

    <!-- Main Content Area -->
    <div class="content-area">
      <div v-if="cartStore.lastScannedItem" class="item-display">
        <!-- Product Image -->
        <v-card class="product-image-card" elevation="4">
          <div class="image-wrapper">
            <v-img
              :src="getImageUrl(cartStore.lastScannedItem)"
              height="400"
              contain
              class="product-image"
            >
              <template v-slot:placeholder>
                <v-row
                  class="fill-height ma-0"
                  align="center"
                  justify="center"
                >
                  <v-icon size="120" color="grey-lighten-2">
                    mdi-package-variant
                  </v-icon>
                </v-row>
              </template>
            </v-img>
          </div>
        </v-card>

        <!-- Product Info -->
        <div class="product-info">
          <h1 class="product-name">{{ cartStore.lastScannedItem.name }}</h1>

          <v-chip
            v-if="cartStore.lastScannedItem.brand"
            color="blue"
            text-color="white"
            class="mb-4"
          >
            {{ cartStore.lastScannedItem.brand }}
          </v-chip>

          <div v-if="cartStore.lastScannedItem.price != null" class="price-display">
            ${{ cartStore.lastScannedItem.price.toFixed(2) }}
          </div>

          <p v-if="cartStore.lastScannedItem.description" class="description">
            {{ cartStore.lastScannedItem.description }}
          </p>

          <!-- Nutrition Grade -->
          <v-chip
            v-if="cartStore.lastScannedItem.nutrition?.nutrition_grade"
            :color="getNutritionColor(cartStore.lastScannedItem.nutrition.nutrition_grade)"
            text-color="white"
            size="large"
            class="mt-2"
          >
            <v-icon start>mdi-food-apple</v-icon>
            Nutrition Score: {{ cartStore.lastScannedItem.nutrition.nutrition_grade.toUpperCase() }}
          </v-chip>

          <!-- Allergens -->
          <div v-if="cartStore.lastScannedItem.allergens?.length" class="allergens mt-4">
            <strong>⚠️ Allergens:</strong>
            <v-chip
              v-for="allergen in cartStore.lastScannedItem.allergens"
              :key="allergen"
              color="error"
              text-color="white"
              class="ma-1"
              small
            >
              {{ allergen }}
            </v-chip>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <v-icon size="200" color="grey-lighten-2">
          mdi-barcode-scan
        </v-icon>
        <h2 class="mt-8 text-grey">Scan an item to begin</h2>
        <p class="text-grey-darken-1 mt-2">
          Use the barcode scanner or search for products
        </p>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <v-btn
        color="primary"
        size="x-large"
        block
        height="80"
        @click="toggleSearch"
        class="mb-4"
      >
        <v-icon start size="32">mdi-magnify</v-icon>
        Search Products
      </v-btn>

      <v-btn
        v-if="cartStore.items.length > 0"
        color="error"
        size="x-large"
        block
        height="80"
        @click="handleClearCart"
        variant="outlined"
      >
        <v-icon start size="32">mdi-delete</v-icon>
        Clear Cart
      </v-btn>
    </div>
  </div>
</template>

<script>
import { inject, ref, watch } from 'vue'
import { useCartStore } from '@/store/cart'
import { useSettingsStore } from '@/store/settings'
import { api } from '@/services/api'
import SettingsPanel from './SettingsPanel.vue'

export default {
  components: {
    SettingsPanel
  },
  setup() {
    const cartStore = useCartStore()
    const settingsStore = useSettingsStore()
    const toggleSearch = inject('toggleSearch')
    const showSettings = ref(false)

    // Close settings panel when a product is scanned
    watch(() => cartStore.lastScannedItem, (newItem) => {
      if (newItem && showSettings.value) {
        showSettings.value = false
      }
    })

    function getImageUrl(product) {
      if (product.images && product.images.length > 0) {
        return api.getImageUrl(product.images[0])
      }
      return product.image_url || ''
    }

    function getNutritionColor(grade) {
      const gradeUpper = grade.toUpperCase()
      const colors = {
        'A': 'success',
        'B': 'light-green',
        'C': 'warning',
        'D': 'orange',
        'E': 'error'
      }
      return colors[gradeUpper] || 'grey'
    }

    function handleClearCart() {
      if (confirm('Are you sure you want to clear the cart?')) {
        cartStore.clearCart()
      }
    }

    return {
      cartStore,
      settingsStore,
      toggleSearch,
      showSettings,
      getImageUrl,
      getNutritionColor,
      handleClearCart
    }
  }
}
</script>

<style >
.item-details-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.content-area {
  margin-top: 64px;
  flex: 1;
  overflow-y: auto;
  padding: 32px 24px 24px 24px;
}

.item-display {
  max-width: 800px;
  margin: 0 auto;
}

.product-image-card {
  margin-bottom: 32px;
  margin-top: 8px;
  border-radius: 16px;
  overflow: hidden;
}

.image-wrapper {
  padding: 16px;
}

.product-image {
  background-color: #f5f5f5;
  border-radius: 8px;
}

.product-info {
  text-align: left;
}

.product-name {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 16px;
  line-height: 1.2;
}

.price-display {
  font-size: 3.5rem;
  font-weight: 800;
  color: #2e7d32;
  margin: 24px 0;
}

.description {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  margin-top: 16px;
}

.allergens {
  padding: 16px;
  background-color: #ffebee;
  border-radius: 8px;
  border-left: 4px solid #f44336;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
}

.action-buttons {
  padding: 24px;
  background-color: #ffffff;
  border-top: 2px solid #e10e0e0;
}

.v-img__img--contain {
  background-color: white !important;
}
</style>
