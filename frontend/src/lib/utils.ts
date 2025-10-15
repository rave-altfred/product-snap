/**
 * Utility functions for common operations
 */

/**
 * Check if the current device is mobile (phone or tablet)
 */
export const isMobileDevice = (): boolean => {
  // Check user agent for mobile indicators
  const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera
  
  // Check for mobile/tablet patterns
  const mobileRegex = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini|mobile/i
  
  // Also check screen size as backup
  const isSmallScreen = window.innerWidth <= 768
  
  // Check for touch capability
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0
  
  return mobileRegex.test(userAgent) || (isSmallScreen && isTouchDevice)
}

/**
 * Check if the current device is specifically a tablet
 */
export const isTabletDevice = (): boolean => {
  const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera
  const tabletRegex = /ipad|android(?!.*mobile)|tablet/i
  const isTabletSize = window.innerWidth >= 768 && window.innerWidth <= 1024
  
  return tabletRegex.test(userAgent) || isTabletSize
}

/**
 * Format file size in human readable format
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

/**
 * Truncate text to specified length with ellipsis
 */
export const truncateText = (text: string, length: number): string => {
  if (text.length <= length) return text
  return text.slice(0, length) + '...'
}