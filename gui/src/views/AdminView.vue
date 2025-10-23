<template>
  <div class="admin-container">
    <!-- Login Form -->
    <div v-if="!isAuthenticated" class="login-card">
      <h1>Admin Login</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Enter username"
            required
            autofocus
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter password"
            required
          />
        </div>
        <button type="submit" class="btn-login" :disabled="isLoggingIn">
          {{ isLoggingIn ? 'Logging in...' : 'Login' }}
        </button>
        <div v-if="loginError" class="error-message">{{ loginError }}</div>
      </form>
    </div>

    <!-- Admin Panel -->
    <div v-else class="admin-panel">
      <div class="admin-header">
        <h1>Product Administration</h1>
        <div class="header-actions">
          <button @click="handleRefresh" class="btn-refresh">
            <span class="refresh-icon">↻</span> Refresh
          </button>
          <button @click="handleLogout" class="btn-logout">Logout</button>
        </div>
      </div>

      <!-- Scanner Input Handler -->
      <ScannerInput admin-mode @product-scanned="handleProductScanned" />

      <!-- Search Bar -->
      <div class="search-section">
        <div class="search-bar">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search products by name or brand..."
            @input="handleSearch"
            class="search-input"
          />
          <button v-if="searchQuery" @click="clearSearch" class="btn-clear-search">✕</button>
        </div>

        <!-- Search Results Dropdown -->
        <div v-if="searchResults.length > 0" class="search-results">
          <div
            v-for="product in searchResults"
            :key="product.id"
            @click="selectProduct(product)"
            class="search-result-item"
          >
            <img
              v-if="product.images && product.images.length > 0"
              :src="getImageUrl(product.images[0])"
              :alt="product.name"
              class="result-thumbnail"
            />
            <div class="result-info">
              <div class="result-name">{{ product.name }}</div>
              <div class="result-details">
                <span v-if="product.brand" class="result-brand">{{ product.brand }}</span>
                <span class="result-upc">UPC: {{ product.upc }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- No Results Message -->
        <div v-if="searchQuery && isSearching === false && searchResults.length === 0" class="no-results">
          No products found matching "{{ searchQuery }}"
        </div>
      </div>

      <!-- Scanning Indicator -->
      <div v-if="isScanning" class="scanning-overlay">
        <div class="scanning-spinner"></div>
        <p>Scanning {{ currentUpc }}...</p>
      </div>

      <!-- Product Editor -->
      <div v-if="currentProduct" class="product-editor">
        <h2>Edit Product</h2>

        <div class="editor-grid">
          <!-- Left Column: Product Details -->
          <div class="editor-section">
            <h3>Product Information</h3>

            <div class="form-group">
              <label>UPC/ISBN</label>
              <input v-model="currentProduct.upc" type="text" readonly />
            </div>

            <div class="form-group">
              <label>Product Name *</label>
              <input v-model="currentProduct.name" type="text" required />
            </div>

            <div class="form-group">
              <label>Brand</label>
              <input v-model="currentProduct.brand" type="text" />
            </div>

            <div class="form-group">
              <label>Price</label>
              <input v-model.number="currentProduct.price" type="number" step="0.01" />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea v-model="currentProduct.description" rows="3"></textarea>
            </div>

            <div class="form-group">
              <label>Tags (comma-separated)</label>
              <input v-model="tagsString" type="text" placeholder="organic, snack, healthy" />
            </div>
          </div>

          <!-- Right Column: Images -->
          <div class="editor-section">
            <h3>Product Images</h3>

            <!-- Current Images -->
            <div v-if="currentProduct.images && currentProduct.images.length > 0" class="current-images">
              <div
                v-for="(imageId, index) in currentProduct.images"
                :key="imageId"
                class="image-preview"
              >
                <img :src="getImageUrl(imageId)" :alt="currentProduct.name" />
                <button @click="removeImage(index)" class="btn-remove-image">×</button>
              </div>
            </div>

            <!-- Add Image Options -->
            <div class="add-image-section">
              <h4>Add Image</h4>

              <div class="paste-hint">
                💡 <strong>Tip:</strong> You can paste images directly from your clipboard!
              </div>

              <div class="form-group">
                <label>Upload Image File</label>
                <input
                  type="file"
                  accept="image/*"
                  @change="handleImageUpload"
                  ref="fileInput"
                />
              </div>

              <div class="divider">OR</div>

              <div class="form-group">
                <label>Image URL</label>
                <div class="url-input-group">
                  <input
                    v-model="imageUrl"
                    type="url"
                    placeholder="https://example.com/image.jpg"
                  />
                  <button @click="handleImageUrlAdd" :disabled="!imageUrl" class="btn-add-url">
                    Add
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="editor-actions">
          <button @click="saveProduct" class="btn-save" :disabled="isSaving">
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </button>
          <button @click="cancelEdit" class="btn-cancel">Cancel</button>
          <button @click="deleteProduct" class="btn-delete" :disabled="isSaving">
            Delete Product
          </button>
        </div>

        <!-- On-Screen Keyboard -->
        <div class="keyboard-section">
          <h3>On-Screen Keyboard</h3>
          <OnScreenKeyboard v-model="keyboardInput" @search="handleKeyboardSearch" />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <p>Scan a product barcode to begin editing</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { api } from '@/services/api'
import type { Product } from '@/types'
import ScannerInput from '@/components/ScannerInput.vue'
import OnScreenKeyboard from '@/components/OnScreenKeyboard.vue'
import { isDebugMode } from '@/utils/urlParams'

const isAuthenticated = ref(false)
const username = ref('')
const password = ref('')
const isLoggingIn = ref(false)
const loginError = ref('')

const currentProduct = ref<Product | null>(null)
const currentUpc = ref('')
const isScanning = ref(false)
const isSaving = ref(false)
const imageUrl = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

// Search functionality
const searchQuery = ref('')
const searchResults = ref<Product[]>([])
const isSearching = ref(false)
let searchTimeout: number | null = null

// Keyboard functionality
const keyboardInput = ref('')

const tagsString = computed({
  get: () => currentProduct.value?.tags?.join(', ') || '',
  set: (value: string) => {
    if (currentProduct.value) {
      currentProduct.value.tags = value.split(',').map(t => t.trim()).filter(t => t)
    }
  }
})

// Check if already authenticated
isAuthenticated.value = api.isAuthenticated()

// Handle paste events for clipboard images
function handlePaste(event: ClipboardEvent) {
  // Only process paste when editing a product
  if (!currentProduct.value) return

  const items = event.clipboardData?.items
  if (!items) return

  // Look for image in clipboard
  for (let i = 0; i < items.length; i++) {
    const item = items[i]

    if (item.type.startsWith('image/')) {
      event.preventDefault()

      const file = item.getAsFile()
      if (file) {
        uploadImageFile(file)
      }
      break
    }
  }
}

// Mount/unmount paste listener
import { onMounted as vueOnMounted, onUnmounted as vueOnUnmounted } from 'vue'

vueOnMounted(() => {
  window.addEventListener('paste', handlePaste)
})

vueOnUnmounted(() => {
  window.removeEventListener('paste', handlePaste)
})

async function handleLogin() {
  isLoggingIn.value = true
  loginError.value = ''

  try {
    await api.login(username.value, password.value)
    isAuthenticated.value = true
  } catch (error: any) {
    loginError.value = error.response?.data?.detail || 'Login failed. Please check your credentials.'
  } finally {
    isLoggingIn.value = false
  }
}

function handleLogout() {
  api.logout()
  isAuthenticated.value = false
  currentProduct.value = null
}

async function handleProductScanned(upc: string) {
  currentUpc.value = upc
  isScanning.value = true

  try {
    // Use cache=false when debug mode is enabled via URL parameter
    const useCache = !isDebugMode()
    console.log(`Admin loading product with cache=${useCache} (debug mode: ${isDebugMode()})`)
    const product = await api.getProductByUPC(upc, useCache)
    currentProduct.value = { ...product }
  } catch (error: any) {
    console.error('Error loading product:', error)
    alert(`Failed to load product: ${error.response?.data?.detail || error.message}`)
  } finally {
    isScanning.value = false
  }
}

function getImageUrl(imageId: string): string {
  return api.getImageUrl(imageId)
}

async function uploadImageFile(file: File) {
  if (!currentProduct.value) return

  try {
    const uploaded = await api.uploadImage(file)

    if (!currentProduct.value.images) {
      currentProduct.value.images = []
    }

    currentProduct.value.images.push(uploaded.id)

    // Show success feedback
    console.log('Image uploaded successfully from clipboard/file')
  } catch (error: any) {
    console.error('Error uploading image:', error)
    alert('Failed to upload image')
  }
}

async function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  await uploadImageFile(file)

  // Reset file input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function handleImageUrlAdd() {
  if (!imageUrl.value || !currentProduct.value) return

  try {
    const imageId = await api.addImageByUrl(imageUrl.value, currentProduct.value.id || '')

    if (!currentProduct.value.images) {
      currentProduct.value.images = []
    }

    currentProduct.value.images.push(imageId)
    imageUrl.value = ''
  } catch (error: any) {
    console.error('Error adding image from URL:', error)
    alert('Failed to add image from URL')
  }
}

function removeImage(index: number) {
  if (currentProduct.value?.images) {
    currentProduct.value.images.splice(index, 1)
  }
}

async function saveProduct() {
  if (!currentProduct.value || !currentProduct.value.id) return

  isSaving.value = true

  try {
    await api.updateProduct(currentProduct.value.id, currentProduct.value)
    console.log('Product saved successfully!')
  } catch (error: any) {
    console.error('Error saving product:', error)
    alert(`Failed to save product: ${error.response?.data?.detail || error.message}`)
  } finally {
    isSaving.value = false
  }
}

function cancelEdit() {
  currentProduct.value = null
}

async function deleteProduct() {
  if (!currentProduct.value || !currentProduct.value.id) return

  const confirmDelete = confirm(
    `Are you sure you want to permanently delete "${currentProduct.value.name}"?\n\nThis action cannot be undone.`
  )

  if (!confirmDelete) return

  isSaving.value = true

  try {
    await api.deleteProduct(currentProduct.value.id)
    console.log('Product deleted successfully!')
    currentProduct.value = null
  } catch (error: any) {
    console.error('Error deleting product:', error)
    alert(`Failed to delete product: ${error.response?.data?.detail || error.message}`)
  } finally {
    isSaving.value = false
  }
}

// Search functionality
function handleSearch() {
  // Clear existing timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  // Clear results if search is empty
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  // Debounce search by 300ms
  searchTimeout = window.setTimeout(async () => {
    await performSearch()
  }, 300)
}

async function performSearch() {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  isSearching.value = true

  try {
    const results = await api.searchProducts(searchQuery.value)
    searchResults.value = results
  } catch (error: any) {
    console.error('Error searching products:', error)
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

function selectProduct(product: Product) {
  currentProduct.value = { ...product }
  searchQuery.value = ''
  searchResults.value = []
}

function clearSearch() {
  searchQuery.value = ''
  searchResults.value = []
}

function handleRefresh() {
  window.location.reload()
}

function handleKeyboardSearch() {
  // Use keyboard input for search
  searchQuery.value = keyboardInput.value
  handleSearch()
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  overflow-y: auto;
}

/* Login Card */
.login-card {
  max-width: 400px;
  margin: 5rem auto;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-card h1 {
  margin-bottom: 1.5rem;
  color: #333;
  text-align: center;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.btn-login {
  width: 100%;
  padding: 0.875rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-login:hover:not(:disabled) {
  background: #5568d3;
}

.btn-login:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fee;
  color: #c33;
  border-radius: 6px;
  text-align: center;
}

/* Admin Panel */
.admin-panel {
  max-width: 1400px;
  margin: 0 auto;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.admin-header h1 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-refresh {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-refresh:hover {
  background: #5568d3;
}

.refresh-icon {
  font-size: 1.2rem;
  display: inline-block;
  animation: spin 2s linear infinite paused;
}

.btn-refresh:active .refresh-icon {
  animation-play-state: running;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn-logout {
  padding: 0.75rem 1.5rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-logout:hover {
  background: #c82333;
}

/* Search Section */
.search-section {
  margin-bottom: 2rem;
  position: relative;
}

.search-bar {
  position: relative;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.search-input {
  width: 100%;
  padding: 1.25rem 3rem 1.25rem 1.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 1.1rem;
  box-sizing: border-box;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.btn-clear-search {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.btn-clear-search:hover {
  background: #c82333;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  max-height: 400px;
  overflow-y: auto;
  z-index: 100;
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.search-result-item:hover {
  background: #f8f9fa;
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
  margin-right: 1rem;
  border: 1px solid #e0e0e0;
}

.result-info {
  flex: 1;
}

.result-name {
  font-weight: 600;
  font-size: 1rem;
  color: #333;
  margin-bottom: 0.25rem;
}

.result-details {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.result-brand {
  font-weight: 500;
}

.result-upc {
  color: #999;
}

.no-results {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  color: #999;
  margin-top: 0.5rem;
}

/* Scanning Overlay */
.scanning-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.scanning-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.scanning-overlay p {
  margin-top: 1rem;
  color: white;
  font-size: 1.2rem;
}

/* Product Editor */
.product-editor {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.product-editor h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.editor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.editor-section h3 {
  margin-bottom: 1rem;
  color: #555;
  font-size: 1.2rem;
}

.current-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.image-preview {
  position: relative;
  aspect-ratio: 1;
  border: 2px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-remove-image {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 30px;
  height: 30px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-remove-image:hover {
  background: #c82333;
}

.add-image-section {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.add-image-section h4 {
  margin-bottom: 1rem;
  color: #333;
}

.paste-hint {
  padding: 0.75rem;
  background: #e3f2fd;
  border-left: 3px solid #2196f3;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #1565c0;
}

.divider {
  text-align: center;
  margin: 1rem 0;
  color: #999;
  font-weight: 600;
}

.url-input-group {
  display: flex;
  gap: 0.5rem;
}

.url-input-group input {
  flex: 1;
}

.btn-add-url {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.btn-add-url:hover:not(:disabled) {
  background: #5568d3;
}

.btn-add-url:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.editor-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-save,
.btn-cancel,
.btn-delete {
  padding: 0.875rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-save {
  background: #28a745;
  color: white;
}

.btn-save:hover:not(:disabled) {
  background: #218838;
}

.btn-save:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-cancel {
  background: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background: #5a6268;
}

.btn-delete {
  background: #dc3545;
  color: white;
  margin-left: auto;
}

.btn-delete:hover:not(:disabled) {
  background: #c82333;
}

.btn-delete:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Empty State */
.empty-state {
  background: white;
  padding: 4rem 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.empty-state p {
  color: #999;
  font-size: 1.2rem;
}

/* Keyboard Section */
.keyboard-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.keyboard-section h3 {
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .editor-grid {
    grid-template-columns: 1fr;
  }
}
</style>
