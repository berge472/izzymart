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
    <ScannerInput />
  </v-container>
</template>

<script setup lang="ts">
import { ref, provide } from 'vue'
import ItemDetails from '@/components/ItemDetails.vue'
import CartList from '@/components/CartList.vue'
import SearchDialog from '@/components/SearchDialog.vue'
import ScannerInput from '@/components/ScannerInput.vue'

const showSearch = ref(false)

// Provide search dialog toggle for child components
provide('toggleSearch', () => {
  showSearch.value = !showSearch.value
})
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
