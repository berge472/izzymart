import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export interface ThemeColor {
  name: string
  primary: string
  secondary: string
  accent: string
}

export const themeColors: ThemeColor[] = [
  {
    name: 'Purple',
    primary: '#667eea',
    secondary: '#764ba2',
    accent: '#f093fb'
  },
  {
    name: 'Blue',
    primary: '#1976D2',
    secondary: '#2196F3',
    accent: '#82B1FF'
  },
  {
    name: 'Green',
    primary: '#11998e',
    secondary: '#38ef7d',
    accent: '#96e6a1'
  },
  {
    name: 'Orange',
    primary: '#fa709a',
    secondary: '#fee140',
    accent: '#ffd89b'
  },
  {
    name: 'Red',
    primary: '#eb3349',
    secondary: '#f45c43',
    accent: '#ff6a6a'
  },
  {
    name: 'Teal',
    primary: '#2dd4bf',
    secondary: '#14b8a6',
    accent: '#5eead4'
  }
]

const STORAGE_KEYS = {
  STORE_NAME: 'izzymart_store_name',
  THEME: 'izzymart_theme',
  CAMERA_SCANNING: 'izzymart_camera_scanning'
}

export const useSettingsStore = defineStore('settings', () => {
  // Load from localStorage or use defaults
  const storeName = ref(localStorage.getItem(STORAGE_KEYS.STORE_NAME) || 'IzzyMart')
  const selectedTheme = ref<ThemeColor>(
    JSON.parse(localStorage.getItem(STORAGE_KEYS.THEME) || 'null') || themeColors[1] // Blue theme is default
  )
  const cameraScanningEnabled = ref(
    localStorage.getItem(STORAGE_KEYS.CAMERA_SCANNING) === 'true' // Default: false
  )

  // Watch for changes and persist to localStorage
  watch(storeName, (newName) => {
    localStorage.setItem(STORAGE_KEYS.STORE_NAME, newName)
  })

  watch(selectedTheme, (newTheme) => {
    localStorage.setItem(STORAGE_KEYS.THEME, JSON.stringify(newTheme))
    applyTheme(newTheme)
  }, { deep: true })

  watch(cameraScanningEnabled, (enabled) => {
    localStorage.setItem(STORAGE_KEYS.CAMERA_SCANNING, enabled.toString())
  })

  // Apply theme CSS variables
  function applyTheme(theme: ThemeColor) {
    const root = document.documentElement
    root.style.setProperty('--color-primary', theme.primary)
    root.style.setProperty('--color-secondary', theme.secondary)
    root.style.setProperty('--color-accent', theme.accent)
  }

  function setStoreName(name: string) {
    storeName.value = name
  }

  function setTheme(theme: ThemeColor) {
    selectedTheme.value = theme
  }

  function setCameraScanning(enabled: boolean) {
    cameraScanningEnabled.value = enabled
  }

  // Apply theme on store creation
  applyTheme(selectedTheme.value)

  return {
    storeName,
    selectedTheme,
    cameraScanningEnabled,
    setStoreName,
    setTheme,
    setCameraScanning,
    themeColors
  }
})
