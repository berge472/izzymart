<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    fullscreen
    transition="dialog-bottom-transition"
  >
    <v-card class="search-card">
      <v-toolbar color="primary" dark>
        <v-btn
          icon
          @click="$emit('update:modelValue', false)"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-toolbar-title>Search Products</v-toolbar-title>
      </v-toolbar>

      <div class="search-container">
        <!-- Search Input Display -->
        <div class="search-input-display">
          <v-text-field
            v-model="searchQuery"
            variant="outlined"
            placeholder="Type product name..."
            hide-details
            readonly
            class="search-field"
            @click="focusKeyboard"
          >
            <template v-slot:append-inner>
              <v-btn
                icon
                @click="clearSearch"
                v-if="searchQuery"
              >
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </template>
          </v-text-field>
        </div>

        <!-- Products Display -->
        <div class="search-results" v-if="displayProducts.length > 0">
          <!-- Grid Layout for Produce Items -->
          <div class="products-grid">
            <div
              v-for="product in displayProducts"
              :key="product.upc"
              class="product-card"
              @click="selectProduct(product)"
            >
              <div class="product-image">
                <v-img
                  :src="getImageUrl(product)"
                  cover
                  aspect-ratio="1"
                >
                  <template v-slot:placeholder>
                    <div class="image-placeholder">
                      <v-icon size="60" color="grey-lighten-1">mdi-food-apple</v-icon>
                    </div>
                  </template>
                </v-img>
              </div>
              <div class="product-info">
                <div class="product-name">{{ product.name }}</div>
                <div class="product-brand">{{ product.brand || 'Generic' }}</div>
                <div class="product-price">${{ product.price.toFixed(2) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- No Results -->
        <div class="no-results" v-else-if="searchQuery.length > 0 && hasSearched">
          <v-icon size="120" color="grey-lighten-2">mdi-magnify-close</v-icon>
          <p class="text-h6 text-grey mt-4">No products found</p>
          <p class="text-grey">Try a different search term</p>
        </div>

        <!-- Loading State -->
        <div class="loading-state" v-else-if="isLoadingProduce">
          <v-progress-circular indeterminate size="64" color="primary"></v-progress-circular>
          <p class="text-h6 text-grey mt-4">Loading produce items...</p>
        </div>

        <!-- Empty State -->
        <div class="empty-state" v-else-if="produceItems.length === 0">
          <v-icon size="120" color="grey-lighten-2">mdi-food-apple-outline</v-icon>
          <p class="text-h6 text-grey mt-4">No produce items available</p>
          <p class="text-grey">Search for other products above</p>
        </div>

        <!-- On-Screen Keyboard -->
        <div class="keyboard-container">
          <OnScreenKeyboard
            v-model="searchQuery"
            @search="handleSearch"
          />
        </div>
      </div>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref, watch, computed, onMounted } from 'vue'
import { useCartStore } from '@/store/cart'
import { api } from '@/services/api'
import OnScreenKeyboard from './OnScreenKeyboard.vue'

export default {
  components: {
    OnScreenKeyboard
  },
  props: {
    modelValue: {
      type: Boolean,
      required: true
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const cartStore = useCartStore()
    const searchQuery = ref('')
    const searchResults = ref([])
    const produceItems = ref([])
    const hasSearched = ref(false)
    const isSearching = ref(false)
    const isLoadingProduce = ref(false)

    // Computed property to determine which products to display
    const displayProducts = computed(() => {
      // If user has typed something, filter produce items
      if (searchQuery.value.trim().length > 0) {
        const query = searchQuery.value.toLowerCase()
        return produceItems.value.filter(product =>
          product.name.toLowerCase().includes(query) ||
          (product.brand && product.brand.toLowerCase().includes(query)) ||
          (product.category && product.category.toLowerCase().includes(query))
        )
      }
      // Otherwise show all produce items
      return produceItems.value
    })

    function getImageUrl(product) {
      if (product.images && product.images.length > 0) {
        return api.getImageUrl(product.images[0])
      }
      return product.image_url || ''
    }

    async function handleSearch() {
      if (searchQuery.value.trim().length < 2) {
        return
      }

      hasSearched.value = true
      isSearching.value = true

      try {
        const results = await api.searchProducts(searchQuery.value)
        searchResults.value = results
      } catch (error) {
        console.error('Search error:', error)
        searchResults.value = []
      } finally {
        isSearching.value = false
      }
    }

    function selectProduct(product) {
      cartStore.addItem(product)
      emit('update:modelValue', false)
      clearSearch()
    }

    function clearSearch() {
      searchQuery.value = ''
      searchResults.value = []
      hasSearched.value = false
    }

    function focusKeyboard() {
      // Keyboard is always visible, nothing to do
    }

    // Load all produce items
    async function loadProduceItems() {
      isLoadingProduce.value = true

      try {
        // Fetch produce items from dedicated endpoint (no auth required)
        produceItems.value = await api.getProduceItems()

        console.log(`Loaded ${produceItems.value.length} produce items`)
      } catch (error) {
        console.error('Error loading produce items:', error)
        produceItems.value = []
      } finally {
        isLoadingProduce.value = false
      }
    }

    // Note: Filtering happens automatically via the displayProducts computed property
    // No need to watch searchQuery for API calls since we filter locally

    // Load produce items when dialog opens
    watch(() => props.modelValue, (isOpen) => {
      if (isOpen && produceItems.value.length === 0) {
        loadProduceItems()
      }
    })

    // Load produce items on mount if dialog is already open
    onMounted(() => {
      if (props.modelValue) {
        loadProduceItems()
      }
    })

    return {
      searchQuery,
      searchResults,
      produceItems,
      hasSearched,
      isSearching,
      isLoadingProduce,
      displayProducts,
      getImageUrl,
      handleSearch,
      selectProduct,
      clearSearch,
      focusKeyboard
    }
  }
}
</script>

<style scoped>
.search-card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.search-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.search-input-display {
  padding: 24px;
  background-color: #f5f5f5;
}

.search-field {
  font-size: 1.5rem;
}

.search-results {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  padding: 8px;
}

.product-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.product-card:active {
  transform: translateY(-2px);
}

.product-image {
  width: 100%;
  aspect-ratio: 1;
  background: #f5f5f5;
  position: relative;
  overflow: hidden;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
}

.product-info {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.product-name {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 2.6em;
}

.product-brand {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 4px;
}

.product-price {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2e7d32;
  margin-top: auto;
}

.no-results,
.empty-state,
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.keyboard-container {
  background-color: #ffffff;
  border-top: 2px solid #e0e0e0;
  padding: 16px;
}
</style>
