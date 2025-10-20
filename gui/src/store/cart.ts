import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CartItem, Product } from '@/types'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const lastScannedItem = ref<Product | null>(null)

  const total = computed(() => {
    return items.value.reduce((sum, item) => {
      return sum + ((item.product.price || 0) * item.quantity)
    }, 0)
  })

  const itemCount = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  function addItem(product: Product) {
    lastScannedItem.value = product

    const existingItem = items.value.find(
      item => item.product.upc === product.upc
    )

    if (existingItem) {
      existingItem.quantity++
    } else {
      items.value.push({
        product,
        quantity: 1,
        timestamp: Date.now()
      })
    }
  }

  function removeItem(upc: string) {
    const index = items.value.findIndex(item => item.product.upc === upc)
    if (index !== -1) {
      if (items.value[index].quantity > 1) {
        items.value[index].quantity--
      } else {
        items.value.splice(index, 1)
      }
    }
  }

  function clearCart() {
    items.value = []
    lastScannedItem.value = null
  }

  function deleteItem(upc: string) {
    const index = items.value.findIndex(item => item.product.upc === upc)
    if (index !== -1) {
      items.value.splice(index, 1)
    }
  }

  return {
    items,
    lastScannedItem,
    total,
    itemCount,
    addItem,
    removeItem,
    clearCart,
    deleteItem
  }
})
