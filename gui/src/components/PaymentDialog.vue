<template>
  <v-dialog
    v-model="isOpen"
    max-width="500px"
    persistent
  >
    <v-card>
      <v-card-title class="text-h5 text-center py-4">
        {{ paymentState === 'approved' ? 'Payment Approved!' : 'Enter PIN' }}
      </v-card-title>

      <v-card-text>
        <!-- Payment Approved State -->
        <div v-if="paymentState === 'approved'" class="text-center py-8">
          <v-icon size="80" color="success">mdi-check-circle</v-icon>
          <h2 class="mt-4 text-h4">Approved</h2>
          <p class="mt-4 text-h6">Thank you for your purchase!</p>
        </div>

        <!-- PIN Entry State -->
        <div v-else>
          <!-- PIN Display -->
          <div class="pin-display">
            <span class="pin-text">{{ pinDisplay }}</span>
          </div>

          <!-- Credit Card Logos -->
          <div class="card-logos">
            <img src="/creditcards.png" alt="Credit Cards" class="creditcards-image">
          </div>

          <!-- Number Pad -->
          <div class="number-pad">
            <v-btn
              v-for="num in [1, 2, 3, 4, 5, 6, 7, 8, 9]"
              :key="num"
              class="number-btn"
              size="x-large"
              color="primary"
              @click="addDigit(num)"
            >
              {{ num }}
            </v-btn>
            <div></div>
            <v-btn
              class="number-btn"
              size="x-large"
              color="primary"
              @click="addDigit(0)"
            >
              0
            </v-btn>
            <div></div>
          </div>

          <!-- Pay Button -->
          <v-btn
            color="success"
            size="x-large"
            block
            class="mt-4 pay-btn"
            :loading="paymentState === 'processing'"
            :disabled="pinLength === 0"
            @click="processPayment"
          >
            <v-icon start>mdi-credit-card</v-icon>
            Pay
          </v-btn>

          <v-btn
            variant="text"
            block
            class="mt-2"
            @click="cancel"
          >
            Cancel
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, defineProps, defineEmits } from 'vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'payment-complete': []
}>()

const isOpen = ref(props.modelValue)
const pin = ref('')
const pinLength = ref(0)
const paymentState = ref<'entry' | 'processing' | 'approved'>('entry')

// Computed property to display PIN as asterisks
const pinDisplay = computed(() => {
  return '*'.repeat(pinLength.value)
})

// Sync with parent
watch(() => props.modelValue, (newValue) => {
  isOpen.value = newValue
  if (newValue) {
    // Reset state when opening
    pin.value = ''
    pinLength.value = 0
    paymentState.value = 'entry'
  }
})

watch(isOpen, (newValue) => {
  emit('update:modelValue', newValue)
})

function addDigit(digit: number) {
  if (pinLength.value < 12) {
    pin.value += digit.toString()
    pinLength.value = pin.value.length
  }
}

function cancel() {
  isOpen.value = false
}

function playCashRegisterSound() {
  // Play the cash register MP3 file
  const audio = new Audio('/cash_register.mp3')
  audio.volume = 0.7
  audio.play().catch(error => {
    console.error('Error playing cash register sound:', error)
  })
}

async function processPayment() {
  paymentState.value = 'processing'

  // Simulate payment processing
  await new Promise(resolve => setTimeout(resolve, 1000))

  // Show approval and play cash register sound
  paymentState.value = 'approved'
  playCashRegisterSound()

  // Wait a bit, then close and emit completion
  setTimeout(() => {
    emit('payment-complete')
    isOpen.value = false
  }, 2500)
}
</script>

<style scoped>
.pin-display {
  padding: 2rem;
  margin-bottom: 1.5rem;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pin-text {
  font-size: 2.5rem;
  font-weight: bold;
  color: #333;
  letter-spacing: 0.5rem;
  text-align: center;
  font-family: monospace;
  min-height: 1em;
}

.card-logos {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.creditcards-image {
  max-width: 100%;
  height: auto;
  max-height: 80px;
}

.number-pad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.number-btn {
  aspect-ratio: 1;
  font-size: 1.5rem;
  font-weight: bold;
  border-radius: 12px !important;
}

.pay-btn {
  font-size: 1.25rem;
  font-weight: bold;
  height: 60px !important;
}
</style>
