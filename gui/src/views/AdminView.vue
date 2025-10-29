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
          <button @click="handleRemoveAll" class="btn-remove-all">
            🗑️ Remove All Products
          </button>
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

      <!-- Recent Products Grid -->
      <div class="recent-products-section">
        <RecentProductsGrid
          @product-selected="selectProduct"
          @product-deleted="handleProductDeleted"
        />
      </div>

      <!-- Product Editor Modal -->
      <ProductEditorModal
        v-model="showProductEditor"
        :product="currentProduct"
        @product-saved="handleProductSaved"
        @product-deleted="handleProductDeleted"
      />

      <!-- OLD Product Editor (keeping as comment for reference, remove later) -->
      <div v-if="false" class="product-editor">
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
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { api } from '@/services/api'
import ScannerInput from '@/components/ScannerInput.vue'
import RecentProductsGrid from '@/components/RecentProductsGrid.vue'
import ProductEditorModal from '@/components/ProductEditorModal.vue'
import { isDebugMode } from '@/utils/urlParams'

export default {
  components: {
    ScannerInput,
    RecentProductsGrid,
    ProductEditorModal
  },
  setup() {
    const isAuthenticated = ref(false)
    const username = ref('')
    const password = ref('')
    const isLoggingIn = ref(false)
    const loginError = ref('')

    const currentProduct = ref(null)
    const showProductEditor = ref(false)
    const currentUpc = ref('')
    const isScanning = ref(false)

    // Search functionality
    const searchQuery = ref('')
    const searchResults = ref([])
    const isSearching = ref(false)
    let searchTimeout = null

    // Check if already authenticated
    isAuthenticated.value = api.isAuthenticated()

    async function handleLogin() {
      isLoggingIn.value = true
      loginError.value = ''

      try {
        await api.login(username.value, password.value)
        isAuthenticated.value = true
      } catch (error) {
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

    async function handleProductScanned(upc) {
      currentUpc.value = upc
      isScanning.value = true

      try {
        // Use cache=false when debug mode is enabled via URL parameter
        const useCache = !isDebugMode()
        console.log(`Admin loading product with cache=${useCache} (debug mode: ${isDebugMode()})`)
        const product = await api.getProductByUPC(upc, useCache)
        currentProduct.value = { ...product }
        showProductEditor.value = true
      } catch (error) {
        console.error('Error loading product:', error)
        alert(`Failed to load product: ${error.response?.data?.detail || error.message}`)
      } finally {
        isScanning.value = false
      }
    }

    function getImageUrl(imageId) {
      return api.getImageUrl(imageId)
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
      } catch (error) {
        console.error('Error searching products:', error)
        searchResults.value = []
      } finally {
        isSearching.value = false
      }
    }

    function selectProduct(product) {
      currentProduct.value = { ...product }
      showProductEditor.value = true
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

    function handleProductSaved(product) {
      console.log('Product saved:', product)
      // Refresh could be handled here if needed
      // For now, the modal closes and the RecentProductsGrid should refresh
    }

    function handleProductDeleted(product) {
      console.log('Product deleted:', product)
      // If the deleted product was being edited, clear the editor
      if (currentProduct.value && currentProduct.value.id === product.id) {
        currentProduct.value = null
        showProductEditor.value = false
      }
    }

    async function handleRemoveAll() {
      const confirmDelete = confirm(
        '⚠️ WARNING: Remove All Products\n\n' +
        'This will permanently delete ALL products and images from the database.\n\n' +
        'This action CANNOT be undone!\n\n' +
        'Are you absolutely sure you want to continue?'
      )

      if (!confirmDelete) return

      // Second confirmation for extra safety
      const secondConfirm = confirm(
        'FINAL CONFIRMATION\n\n' +
        'This is your last chance to cancel.\n\n' +
        'Click OK to permanently delete ALL products and images.'
      )

      if (!secondConfirm) return

      try {
        const result = await api.resetDatabase()
        console.log('Database reset:', result)

        // Clear current product if any
        currentProduct.value = null

        // Show success message
        alert(
          'Database Reset Complete\n\n' +
          `Deleted:\n` +
          `- ${result.deleted.products} products\n` +
          `- ${result.deleted.file_metadata} file metadata records\n` +
          `- ${result.deleted.gridfs_files} files from storage\n\n` +
          'The page will now refresh.'
        )

        // Refresh the page to reload the empty state
        window.location.reload()
      } catch (error) {
        console.error('Error resetting database:', error)
        alert(`Failed to reset database: ${error.response?.data?.detail || error.message}`)
      }
    }

    return {
      isAuthenticated,
      username,
      password,
      isLoggingIn,
      loginError,
      currentProduct,
      showProductEditor,
      currentUpc,
      isScanning,
      searchQuery,
      searchResults,
      isSearching,
      handleLogin,
      handleLogout,
      handleProductScanned,
      getImageUrl,
      handleSearch,
      performSearch,
      selectProduct,
      clearSearch,
      handleRefresh,
      handleProductSaved,
      handleProductDeleted,
      handleRemoveAll
    }
  }
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

.btn-remove-all {
  padding: 0.75rem 1.5rem;
  background: #ff6b6b;
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

.btn-remove-all:hover {
  background: #ee5a52;
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

/* Recent Products Section */
.recent-products-section {
  margin-bottom: 2rem;
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
