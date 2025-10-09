import { Page, expect } from '@playwright/test';

/**
 * Helper functions for common test operations
 */

/**
 * Check if an element is visible in the viewport
 */
export async function isInViewport(page: Page, selector: string): Promise<boolean> {
  return await page.locator(selector).isInViewport();
}

/**
 * Wait for page to be fully loaded
 */
export async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle');
  await page.waitForLoadState('domcontentloaded');
}

/**
 * Take a full page screenshot with a specific name
 */
export async function takeFullPageScreenshot(page: Page, name: string) {
  await page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
}

/**
 * Verify responsive behavior by checking element visibility
 */
export async function verifyResponsiveLayout(page: Page, isMobile: boolean) {
  if (isMobile) {
    // Mobile layouts typically have hamburger menus
    const mobileMenu = page.getByRole('button', { name: /menu|navigation/i });
    await expect(mobileMenu).toBeVisible();
  } else {
    // Desktop layouts show full navigation
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
  }
}

/**
 * Upload a file using file input
 */
export async function uploadFile(page: Page, fileInputSelector: string, filePath: string) {
  const fileInput = page.locator(fileInputSelector);
  await fileInput.setInputFiles(filePath);
}

/**
 * Create a test image file for upload testing
 */
export function createTestImagePath(filename: string = 'test-image.jpg'): string {
  // Returns path to test fixtures
  return `tests/fixtures/images/${filename}`;
}

/**
 * Wait for API response
 */
export async function waitForApiResponse(page: Page, urlPattern: string | RegExp) {
  return await page.waitForResponse(response => {
    const url = response.url();
    if (typeof urlPattern === 'string') {
      return url.includes(urlPattern);
    }
    return urlPattern.test(url);
  });
}

/**
 * Check if element has specific CSS class
 */
export async function hasClass(page: Page, selector: string, className: string): Promise<boolean> {
  const element = page.locator(selector);
  const classes = await element.getAttribute('class');
  return classes?.includes(className) || false;
}

/**
 * Verify theme is correctly applied
 */
export async function verifyTheme(page: Page, theme: 'light' | 'dark') {
  // Check if the html or body has the appropriate theme class
  const html = page.locator('html');
  const hasThemeClass = await html.evaluate((el, expectedTheme) => {
    return el.classList.contains(expectedTheme) || 
           el.classList.contains(`theme-${expectedTheme}`) ||
           document.body.classList.contains(expectedTheme);
  }, theme);
  
  expect(hasThemeClass || await page.evaluate(() => 
    window.matchMedia('(prefers-color-scheme: dark)').matches
  )).toBeTruthy();
}

/**
 * Scroll to element
 */
export async function scrollToElement(page: Page, selector: string) {
  await page.locator(selector).scrollIntoViewIfNeeded();
}

/**
 * Check if user is authenticated by checking for auth tokens or user menu
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  // Check localStorage for auth token
  const hasToken = await page.evaluate(() => {
    return !!localStorage.getItem('access_token');
  });
  
  return hasToken;
}

/**
 * Log out the current user
 */
export async function logout(page: Page) {
  // Look for logout button or link
  const logoutButton = page.getByRole('button', { name: /logout|sign out/i })
    .or(page.getByRole('link', { name: /logout|sign out/i }));
  
  if (await logoutButton.isVisible()) {
    await logoutButton.click();
    await page.waitForURL('/');
  }
}

/**
 * Fill form field by label
 */
export async function fillFormField(page: Page, label: string | RegExp, value: string) {
  await page.getByLabel(label).fill(value);
}

/**
 * Check for error messages
 */
export async function hasErrorMessage(page: Page, message?: string): Promise<boolean> {
  if (message) {
    return await page.getByText(message).isVisible();
  }
  // Check for common error indicators
  const errorElement = page.locator('[role="alert"], .error, .error-message');
  return await errorElement.isVisible();
}
