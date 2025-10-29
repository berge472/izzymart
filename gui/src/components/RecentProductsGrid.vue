<template>
  <div class="recent-products-grid">
    <h3 class="grid-title">Recently Added/Modified Products</h3>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading products...</p>
    </div>

    <div v-else-if="products.length === 0" class="empty-state">
      <p>No products found</p>
    </div>

    <div v-else class="products-grid">
      <div
        v-for="product in products"
        :key="product.id"
        class="product-card"
        @click="selectProduct(product)"
      >
        <div class="product-image-container">
          <img
            v-if="product.images && product.images.length > 0"
            :src="getImageUrl(product.images[0])"
            :alt="product.name"
            class="product-image"
          />
          <div v-else class="no-image">
            <span>📦</span>
          </div>
        </div>

        <div class="product-info">
          <div class="product-name">{{ product.name }}</div>
          <div v-if="product.brand" class="product-brand">{{ product.brand }}</div>
          <div v-if="product.price" class="product-price">${{ product.price.toFixed(2) }}</div>
        </div>

        <button
          class="btn-delete"
          @click.stop="handleDelete(product)"
          title="Delete product"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'

export default {
  emits: ['product-selected', 'product-deleted'],
  setup(props, { emit }) {
    const products = ref([])
    const loading = ref(true)

    async function loadRecentProducts() {
      loading.value = true
      try {
        const recentProducts = await api.getRecentProducts(100)
        products.value = recentProducts
      } catch (error) {
        console.error('Error loading recent products:', error)
        products.value = []
      } finally {
        loading.value = false
      }
    }

    function getImageUrl(imageId) {
      return api.getImageUrl(imageId)
    }

    function selectProduct(product) {
      emit('product-selected', product)
    }

    async function handleDelete(product) {
      const confirmDelete = confirm(
        `Are you sure you want to delete "${product.name}"?\n\nThis action cannot be undone.`
      )

      if (!confirmDelete) return

      try {
        await api.deleteProduct(product.id)
        // Remove from local list
        products.value = products.value.filter(p => p.id !== product.id)
        emit('product-deleted', product)
      } catch (error) {
        console.error('Error deleting product:', error)
        alert(`Failed to delete product: ${error.response?.data?.detail || error.message}`)
      }
    }

    onMounted(() => {
      loadRecentProducts()
    })

    return {
      products,
      loading,
      getImageUrl,
      selectProduct,
      handleDelete
    }
  }
}
</script>

<style scoped>
.recent-products-grid {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.grid-title {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.3rem;
  font-weight: 600;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #999;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
  font-size: 1.1rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  max-height: 600px;
  overflow-y: auto;
}

.product-card {
  position: relative;
  background: #f8f9fa;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.product-image-container {
  width: 100%;
  aspect-ratio: 1;
  margin-bottom: 0.5rem;
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  font-size: 3rem;
  color: #ccc;
}

.product-info {
  flex: 1;
}

.product-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-brand {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.product-price {
  font-size: 0.85rem;
  font-weight: 700;
  color: #2e7d32;
}

.btn-delete {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 28px;
  height: 28px;
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
  opacity: 0;
  transition: all 0.2s;
  z-index: 10;
}

.product-card:hover .btn-delete {
  opacity: 1;
}

.btn-delete:hover {
  background: #c82333;
  transform: scale(1.1);
}
</style>
