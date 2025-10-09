import { test, expect } from '@playwright/test';
import { waitForPageLoad } from './utils/test-helpers';

test.describe('Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await waitForPageLoad(page);
  });

  test('should display landing page with key elements', async ({ page }) => {
    // Check for main heading (there may be multiple h1 tags)
    await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible();
    
    // Check for call-to-action buttons
    const ctaButtons = page.getByRole('link', { name: /get started|sign up|try free/i });
    await expect(ctaButtons.first()).toBeVisible();
    
    // Check for login link
    const loginLink = page.getByRole('link', { name: /login|sign in/i });
    await expect(loginLink).toBeVisible();
  });

  test('should navigate to login page', async ({ page }) => {
    await page.getByRole('link', { name: /login|sign in/i }).click();
    await expect(page).toHaveURL(/\/login/);
  });

  test('should navigate to register page', async ({ page }) => {
    const signupLink = page.getByRole('link', { name: /get started|sign up|register/i }).first();
    await signupLink.click();
    await expect(page).toHaveURL(/\/(register|signup)/);
  });

  test('should be responsive on mobile', async ({ page, isMobile }) => {
    if (!isMobile) {
      test.skip();
    }
    
    // Verify content is visible on mobile
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    
    // Check viewport width
    const viewport = page.viewportSize();
    expect(viewport?.width).toBeLessThan(768);
  });

  test('should display proper metadata', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/productsnap|product snap/i);
    
    // Check for meta description
    const metaDescription = page.locator('meta[name="description"]');
    await expect(metaDescription).toHaveCount(1);
  });
});
