<template>
  <v-dialog
    v-model="isOpen"
    max-width="1200px"
    persistent
    scrollable
  >
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="text-h5">Edit Product</span>
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="cancel"
        ></v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text class="pa-6">
        <div class="editor-grid">
          <!-- Left Column: Product Details -->
          <div class="editor-section">
            <h3>Product Information</h3>

            <div class="form-group">
              <label>UPC/ISBN</label>
              <input v-model="localProduct.upc" type="text" readonly />
            </div>

            <div class="form-group">
              <label>Product Name *</label>
              <input v-model="localProduct.name" type="text" required />
            </div>

            <div class="form-group">
              <label>Brand</label>
              <input v-model="localProduct.brand" type="text" />
            </div>

            <div class="form-group">
              <label>Price</label>
              <input v-model.number="localProduct.price" type="number" step="0.01" />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea v-model="localProduct.description" rows="3"></textarea>
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
            <div v-if="localProduct.images && localProduct.images.length > 0" class="current-images">
              <div
                v-for="(imageId, index) in localProduct.images"
                :key="imageId"
                class="image-preview"
              >
                <img :src="getImageUrl(imageId)" :alt="localProduct.name" />
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
     </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="pa-4">
        <v-btn
          color="error"
          variant="outlined"
          @click="deleteProduct"
          :disabled="isSaving"
        >
          <v-icon start>mdi-delete</v-icon>
          Delete Product
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          variant="text"
          @click="cancel"
        >
          Cancel
        </v-btn>
        <v-btn
          color="success"
          @click="saveProduct"
          :loading="isSaving"
        >
          <v-icon start>mdi-content-save</v-icon>
          Save Changes
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
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
    },
    product: {
      type: Object,
      default: null
    }
  },
  emits: ['update:modelValue', 'product-saved', 'product-deleted'],
  setup(props, { emit }) {
    const isOpen = ref(props.modelValue)
    const localProduct = ref({ ...props.product })
    const isSaving = ref(false)
    const imageUrl = ref('')
    const fileInput = ref(null)
    const keyboardInput = ref('')

    const tagsString = computed({
      get: () => localProduct.value?.tags?.join(', ') || '',
      set: (value) => {
        if (localProduct.value) {
          localProduct.value.tags = value.split(',').map(t => t.trim()).filter(t => t)
        }
      }
    })

    // Sync with parent
    watch(() => props.modelValue, (newValue) => {
      isOpen.value = newValue
      if (newValue && props.product) {
        // Reset local product when opening
        localProduct.value = { ...props.product }
        imageUrl.value = ''
        keyboardInput.value = ''
      }
    })

    watch(isOpen, (newValue) => {
      emit('update:modelValue', newValue)
    })

    // Handle paste events for clipboard images
    function handlePaste(event) {
      // Only process paste when dialog is open
      if (!isOpen.value) return

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
    onMounted(() => {
      window.addEventListener('paste', handlePaste)
    })

    onUnmounted(() => {
      window.removeEventListener('paste', handlePaste)
    })

    function getImageUrl(imageId) {
      return api.getImageUrl(imageId)
    }

    async function uploadImageFile(file) {
      if (!localProduct.value) return

      try {
        const uploaded = await api.uploadImage(file)

        if (!localProduct.value.images) {
          localProduct.value.images = []
        }

        localProduct.value.images.push(uploaded.id)

        console.log('Image uploaded successfully')
      } catch (error) {
        console.error('Error uploading image:', error)
        alert('Failed to upload image')
      }
    }

    async function handleImageUpload(event) {
      const target = event.target
      const file = target.files?.[0]

      if (!file) return

      await uploadImageFile(file)

      // Reset file input
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    async function handleImageUrlAdd() {
      if (!imageUrl.value || !localProduct.value) return

      try {
        const imageId = await api.addImageByUrl(imageUrl.value, localProduct.value.id || '')

        if (!localProduct.value.images) {
          localProduct.value.images = []
        }

        localProduct.value.images.push(imageId)
        imageUrl.value = ''
      } catch (error) {
        console.error('Error adding image from URL:', error)
        alert('Failed to add image from URL')
      }
    }

    function removeImage(index) {
      if (localProduct.value?.images) {
        localProduct.value.images.splice(index, 1)
      }
    }

    async function saveProduct() {
      if (!localProduct.value || !localProduct.value.id) return

      isSaving.value = true

      try {
        await api.updateProduct(localProduct.value.id, localProduct.value)
        console.log('Product saved successfully!')
        emit('product-saved', localProduct.value)
        isOpen.value = false
      } catch (error) {
        console.error('Error saving product:', error)
        alert(`Failed to save product: ${error.response?.data?.detail || error.message}`)
      } finally {
        isSaving.value = false
      }
    }

    function cancel() {
      isOpen.value = false
    }

    async function deleteProduct() {
      if (!localProduct.value || !localProduct.value.id) return

      const confirmDelete = confirm(
        `Are you sure you want to permanently delete "${localProduct.value.name}"?\n\nThis action cannot be undone.`
      )

      if (!confirmDelete) return

      isSaving.value = true

      try {
        await api.deleteProduct(localProduct.value.id)
        console.log('Product deleted successfully!')
        emit('product-deleted', localProduct.value)
        isOpen.value = false
      } catch (error) {
        console.error('Error deleting product:', error)
        alert(`Failed to delete product: ${error.response?.data?.detail || error.message}`)
      } finally {
        isSaving.value = false
      }
    }

    function handleKeyboardSearch() {
      // Keyboard input can be used for searching or editing
      // This is a placeholder for future functionality
    }

    return {
      isOpen,
      localProduct,
      isSaving,
      imageUrl,
      fileInput,
      keyboardInput,
      tagsString,
      getImageUrl,
      uploadImageFile,
      handleImageUpload,
      handleImageUrlAdd,
      removeImage,
      saveProduct,
      cancel,
      deleteProduct,
      handleKeyboardSearch
    }
  }
}
</script>

<style scoped>
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
