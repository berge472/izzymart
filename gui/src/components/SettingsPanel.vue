<template>
  <v-navigation-drawer
    v-model="isOpen"
    temporary
    location="left"
    width="400"
  >
    <div class="settings-panel">
      <div class="settings-header">
        <h2>Store Settings</h2>
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="close"
        ></v-btn>
      </div>

      <v-divider></v-divider>

      <div class="settings-content">
        <!-- Store Name -->
        <div class="setting-section">
          <h3 class="setting-label">
            <v-icon>mdi-store</v-icon>
            Store Name
          </h3>
          <v-text-field
            v-model="localStoreName"
            variant="outlined"
            density="comfortable"
            placeholder="Enter store name"
            hide-details
          ></v-text-field>
          <p class="setting-hint">This name appears in the header</p>
        </div>

        <!-- Camera Scanning -->
        <div class="setting-section">
          <h3 class="setting-label">
            <v-icon>mdi-camera</v-icon>
            Camera Scanning
          </h3>
          <v-switch
            v-model="localCameraScanning"
            color="primary"
            hide-details
            label="Enable camera barcode scanning"
          ></v-switch>
          <p class="setting-hint">When enabled, a camera button will appear to scan barcodes using your device's camera</p>
        </div>

        <!-- Theme Colors -->
        <div class="setting-section">
          <h3 class="setting-label">
            <v-icon>mdi-palette</v-icon>
            Color Theme
          </h3>
          <div class="theme-grid">
            <div
              v-for="theme in settingsStore.themeColors"
              :key="theme.name"
              class="theme-option"
              :class="{ active: isThemeSelected(theme) }"
              @click="selectTheme(theme)"
            >
              <div class="theme-colors">
                <div
                  class="color-swatch primary"
                  :style="{ backgroundColor: theme.primary }"
                ></div>
                <div
                  class="color-swatch secondary"
                  :style="{ backgroundColor: theme.secondary }"
                ></div>
                <div
                  class="color-swatch accent"
                  :style="{ backgroundColor: theme.accent }"
                ></div>
              </div>
              <div class="theme-name">{{ theme.name }}</div>
              <v-icon
                v-if="isThemeSelected(theme)"
                class="check-icon"
                color="success"
              >
                mdi-check-circle
              </v-icon>
            </div>
          </div>
        </div>

        <!-- Preview -->
        <div class="setting-section">
          <h3 class="setting-label">
            <v-icon>mdi-eye</v-icon>
            Preview
          </h3>
          <div class="preview-card">
            <div class="preview-header">
              <v-icon size="24" class="mr-2">mdi-storefront</v-icon>
              {{ localStoreName }}
            </div>
            <div class="preview-content">
              <div class="preview-button">Sample Button</div>
            </div>
          </div>
        </div>

        <!-- System Info -->
        <div class="setting-section">
          <h3 class="setting-label">
            <v-icon>mdi-information</v-icon>
            System
          </h3>
          <div class="system-info">
            <div class="info-row">
              <span class="info-label">Version:</span>
              <span class="info-value">{{ appVersion }}</span>
            </div>
            <v-btn
              color="primary"
              variant="outlined"
              prepend-icon="mdi-refresh"
              block
              @click="handleRefresh"
            >
              Refresh Page
            </v-btn>
          </div>
        </div>
      </div>

      <div class="settings-footer">
        <v-btn
          color="primary"
          block
          size="large"
          @click="saveSettings"
        >
          <v-icon start>mdi-content-save</v-icon>
          Save Changes
        </v-btn>
      </div>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue'
import { useSettingsStore, type ThemeColor } from '@/store/settings'

const settingsStore = useSettingsStore()

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const isOpen = ref(props.modelValue)
const localStoreName = ref(settingsStore.storeName)
const localTheme = ref<ThemeColor>(settingsStore.selectedTheme)
const localCameraScanning = ref(settingsStore.cameraScanningEnabled)

// App version from package.json
const appVersion = ref('v0.1.0')

// Sync with parent
watch(() => props.modelValue, (newValue) => {
  isOpen.value = newValue
  if (newValue) {
    // Reset local values when opening
    localStoreName.value = settingsStore.storeName
    localTheme.value = settingsStore.selectedTheme
    localCameraScanning.value = settingsStore.cameraScanningEnabled
  }
})

watch(isOpen, (newValue) => {
  emit('update:modelValue', newValue)
})

function close() {
  isOpen.value = false
}

function isThemeSelected(theme: ThemeColor): boolean {
  return theme.name === localTheme.value.name
}

function selectTheme(theme: ThemeColor) {
  localTheme.value = theme
  // Apply immediately for preview
  const root = document.documentElement
  root.style.setProperty('--color-primary', theme.primary)
  root.style.setProperty('--color-secondary', theme.secondary)
  root.style.setProperty('--color-accent', theme.accent)
}

function saveSettings() {
  settingsStore.setStoreName(localStoreName.value)
  settingsStore.setTheme(localTheme.value)
  settingsStore.setCameraScanning(localCameraScanning.value)
  close()
}

function handleRefresh() {
  window.location.reload()
}
</script>

<style scoped>
.settings-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.settings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
}

.settings-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.setting-section {
  margin-bottom: 2rem;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.setting-hint {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #666;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.theme-option {
  position: relative;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.theme-option:hover {
  border-color: #999;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.theme-option.active {
  border-color: var(--color-primary);
  background-color: rgba(102, 126, 234, 0.05);
}

.theme-colors {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.color-swatch {
  flex: 1;
  height: 40px;
  border-radius: 4px;
}

.theme-name {
  text-align: center;
  font-weight: 600;
  color: #333;
}

.check-icon {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}

.preview-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
}

.preview-content {
  padding: 1rem;
}

.preview-button {
  padding: 0.75rem 1.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 6px;
  text-align: center;
  font-weight: 600;
}

.settings-footer {
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.info-label {
  font-weight: 600;
  color: #666;
}

.info-value {
  font-weight: 500;
  color: #333;
  font-family: monospace;
}
</style>
