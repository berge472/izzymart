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

        <!-- Search Results -->
        <div class="search-results" v-if="searchResults.length > 0">
          <v-list class="results-list">
            <v-list-item
              v-for="product in searchResults"
              :key="product.upc"
              class="result-item"
              @click="selectProduct(product)"
            >
              <template v-slot:prepend>
                <v-avatar size="80" rounded="lg">
                  <v-img
                    :src="getImageUrl(product)"
                    cover
                  >
                    <template v-slot:placeholder>
                      <v-icon size="40" color="grey">mdi-package-variant</v-icon>
                    </template>
                  </v-img>
                </v-avatar>
              </template>

              <v-list-item-title class="product-name">
                {{ product.name }}
              </v-list-item-title>

              <v-list-item-subtitle>
                {{ product.brand || 'Generic' }}
              </v-list-item-subtitle>

              <template v-slot:append>
                <div class="product-price">
                  ${{ product.price.toFixed(2) }}
                </div>
              </template>
            </v-list-item>
          </v-list>
        </div>

        <!-- No Results -->
        <div class="no-results" v-else-if="searchQuery.length > 0 && hasSearched">
          <v-icon size="120" color="grey-lighten-2">mdi-magnify-close</v-icon>
          <p class="text-h6 text-grey mt-4">No products found</p>
          <p class="text-grey">Try a different search term</p>
        </div>

        <!-- Empty State -->
        <div class="empty-state" v-else>
          <v-icon size="120" color="grey-lighten-2">mdi-magnify</v-icon>
          <p class="text-h6 text-grey mt-4">Search for products</p>
          <p class="text-grey">Use the keyboard below to type</p>
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

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue'
import { useCartStore } from '@/store/cart'
import { api } from '@/services/api'
import type { Product } from '@/types'
import OnScreenKeyboard from './OnScreenKeyboard.vue'

defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const cartStore = useCartStore()
const searchQuery = ref('')
const searchResults = ref<Product[]>([])
const hasSearched = ref(false)
const isSearching = ref(false)

function getImageUrl(product: Product): string {
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

function selectProduct(product: Product) {
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

// Auto-search when query changes
watch(searchQuery, () => {
  if (searchQuery.value.trim().length >= 2) {
    handleSearch()
  } else {
    searchResults.value = []
    hasSearched.value = false
  }
})
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

.results-list {
  background-color: #ffffff;
  border-radius: 12px;
}

.result-item {
  padding: 16px !important;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.result-item:hover {
  background-color: #f5f5f5;
}

.result-item:last-child {
  border-bottom: none;
}

.product-name {
  font-size: 1.2rem;
  font-weight: 600;
}

.product-price {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2e7d32;
}

.no-results,
.empty-state {
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
