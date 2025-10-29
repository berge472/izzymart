<template>
  <div class="cart-list-container">
    <!-- Payment Dialog -->
    <PaymentDialog
      v-model="showPaymentDialog"
      @payment-complete="onPaymentComplete"
    />

    <!-- Cart Header -->
    <div class="cart-header">
      <h2 class="cart-title">
        <v-icon size="28" class="mr-2">mdi-cart</v-icon>
        Your Cart
      </h2>
      <v-chip color="primary" text-color="white">
        {{ cartStore.itemCount }} items
      </v-chip>
    </div>

    <!-- Cart Items -->
    <div class="cart-items" ref="cartItemsContainer">
      <v-list v-if="cartStore.items.length > 0" class="cart-list">
        <v-list-item
          v-for="item in cartStore.items"
          :key="item.product.upc"
          class="cart-item"
        >
          <template v-slot:prepend>
            <v-avatar size="80" rounded="lg" class="item-thumbnail">
              <v-img
                :src="getImageUrl(item.product)"
                cover
              >
                <template v-slot:placeholder>
                  <v-icon size="40" color="grey">mdi-package-variant</v-icon>
                </template>
              </v-img>
            </v-avatar>
          </template>

          <v-list-item-title class="item-name">
            {{ item.product.name }}
          </v-list-item-title>

          <v-list-item-subtitle class="item-brand">
            {{ item.product.brand || 'Generic' }}
          </v-list-item-subtitle>

          <template v-slot:append>
            <div class="item-controls">
              <div class="quantity-controls">
                <v-btn
                  icon
                  size="small"
                  color="error"
                  variant="text"
                  @click="cartStore.removeItem(item.product.upc)"
                >
                  <v-icon>mdi-minus</v-icon>
                </v-btn>

                <span class="quantity">{{ item.quantity }}</span>

                <v-btn
                  icon
                  size="small"
                  color="success"
                  variant="text"
                  @click="cartStore.addItem(item.product)"
                >
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </div>

              <div class="item-price">
                ${{ (item.product.price * item.quantity).toFixed(2) }}
              </div>

              <v-btn
                icon
                size="small"
                color="error"
                variant="text"
                @click="cartStore.deleteItem(item.product.upc)"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </div>
          </template>
        </v-list-item>

        <v-divider></v-divider>
      </v-list>

      <div v-else class="empty-cart">
        <v-icon size="100" color="grey-lighten-2">mdi-cart-outline</v-icon>
        <p class="text-grey mt-4">Your cart is empty</p>
      </div>
    </div>

    <!-- Cart Total -->
    <div class="cart-total-section">
      <v-divider class="mb-4"></v-divider>

      <div class="total-row">
        <span class="total-label">Subtotal:</span>
        <span class="total-amount">${{ cartStore.total.toFixed(2) }}</span>
      </div>

      <div class="total-row">
        <span class="total-label">Tax (7%):</span>
        <span class="total-amount">${{ (cartStore.total * 0.07).toFixed(2) }}</span>
      </div>

      <v-divider class="my-3"></v-divider>

      <div class="total-row grand-total">
        <span class="total-label">Total:</span>
        <span class="total-amount">${{ (cartStore.total * 1.07).toFixed(2) }}</span>
      </div>

      <v-btn
        color="success"
        size="x-large"
        block
        height="80"
        class="mt-6"
        :disabled="cartStore.items.length === 0"
        @click="handleCheckout"
      >
        <v-icon start size="32">mdi-cash-register</v-icon>
        Checkout
      </v-btn>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick } from 'vue'
import { useCartStore } from '@/store/cart'
import { api } from '@/services/api'
import PaymentDialog from './PaymentDialog.vue'

export default {
  components: {
    PaymentDialog
  },
  setup() {
    const cartStore = useCartStore()
    const showPaymentDialog = ref(false)
    const cartItemsContainer = ref(null)

    function getImageUrl(product) {
      if (product.images && product.images.length > 0) {
        return api.getImageUrl(product.images[0])
      }
      return product.image_url || ''
    }

    function handleCheckout() {
      showPaymentDialog.value = true
    }

    // Auto-scroll to bottom when cart items change
    watch(
      () => cartStore.items.length,
      async () => {
        await nextTick()
        if (cartItemsContainer.value) {
          cartItemsContainer.value.scrollTo({
            top: cartItemsContainer.value.scrollHeight,
            behavior: 'smooth'
          })
        }
      }
    )

    function onPaymentComplete() {
      // Clear the cart after successful payment
      cartStore.clearCart()
    }

    // Watch for changes in cart items and scroll to top when items are added
    watch(() => cartStore.itemCount, async (newCount, oldCount) => {
      if (newCount > oldCount && cartItemsContainer.value) {
        // Item was added, scroll to top to show the most recent item
        await nextTick()
        cartItemsContainer.value.scrollTo({
          top: 0,
          behavior: 'smooth'
        })
      }
    })

    return {
      cartStore,
      showPaymentDialog,
      cartItemsContainer,
      getImageUrl,
      handleCheckout,
      onPaymentComplete
    }
  }
}
</script>

<style scoped>
.cart-list-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #fafafa;
}

.cart-header {
  padding: 24px;
  background-color: #ffffff;
  border-bottom: 2px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cart-title {
  font-size: 1.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  margin: 0;
}

.cart-items {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.cart-list {
  background-color: #ffffff;
  border-radius: 12px;
}

.cart-item {
  padding: 16px !important;
  border-bottom: 1px solid #f0f0f0;
}

.cart-item:last-child {
  border-bottom: none;
}

.item-thumbnail {
  margin-right: 16px;
  border: 2px solid #e0e0e0;
}

.item-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a1a1a;
  white-space: normal;
  line-height: 1.3;
}

.item-brand {
  font-size: 0.9rem;
  color: #666;
  margin-top: 4px;
}

.item-controls {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 4px 8px;
}

.quantity {
  font-size: 1.2rem;
  font-weight: 700;
  min-width: 32px;
  text-align: center;
}

.item-price {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2e7d32;
}

.empty-cart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.cart-total-section {
  padding: 24px;
  background-color: #ffffff;
  border-top: 2px solid #e0e0e0;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.total-label {
  font-size: 1.1rem;
  color: #666;
}

.total-amount {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1a1a1a;
}

.grand-total .total-label {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
}

.grand-total .total-amount {
  font-size: 2rem;
  font-weight: 800;
  color: #2e7d32;
}
</style>
