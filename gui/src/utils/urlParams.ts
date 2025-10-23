/**
 * Utility functions for reading URL parameters
 */

/**
 * Get a URL parameter value by name
 * @param name - The name of the parameter
 * @returns The parameter value or null if not found
 */
export function getUrlParam(name: string): string | null {
  const params = new URLSearchParams(window.location.search)
  return params.get(name)
}

/**
 * Get a boolean URL parameter value
 * @param name - The name of the parameter
 * @param defaultValue - Default value if parameter not found (default: false)
 * @returns true if param is "true", "1", or "yes" (case insensitive)
 */
export function getBooleanUrlParam(name: string, defaultValue: boolean = false): boolean {
  const value = getUrlParam(name)
  if (value === null) {
    return defaultValue
  }
  const lowerValue = value.toLowerCase()
  return lowerValue === 'true' || lowerValue === '1' || lowerValue === 'yes'
}

/**
 * Check if debug mode is enabled via URL parameter
 * Checks for ?debug=true or ?debug=1
 */
export function isDebugMode(): boolean {
  return getBooleanUrlParam('debug', false)
}

/**
 * Get all URL parameters as an object
 */
export function getAllUrlParams(): Record<string, string> {
  const params = new URLSearchParams(window.location.search)
  const result: Record<string, string> = {}
  params.forEach((value, key) => {
    result[key] = value
  })
  return result
}
