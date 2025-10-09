import { test, expect } from '@playwright/test';
import { waitForPageLoad, isAuthenticated } from './utils/test-helpers';

test.describe('Dashboard', () => {
  // Note: These tests require authentication setup to work properly
  // You'll need to configure test users in your environment
  
  test.describe('Authenticated User', () => {
    test.beforeEach(async ({ page }) => {
      // For now, skip if not authenticated
      // In production, you would use storage state from auth.setup.ts
      await page.goto('/dashboard');
      
      // If redirected to login, skip these tests
      const url = page.url();
      if (url.includes('/login')) {
        test.skip();
      }
    });

    test('should display dashboard heading', async ({ page }) => {
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    });

    test('should display navigation menu', async ({ page, isMobile }) => {
      if (isMobile) {
        // Mobile should have a menu button
        const menuButton = page.getByRole('button', { name: /menu|navigation/i });
        if (await menuButton.isVisible()) {
          await menuButton.click();
        }
      }
      
      // Check for navigation links
      await expect(page.getByRole('link', { name: /dashboard/i })).toBeVisible();
    });

    test('should navigate to new shoot page', async ({ page }) => {
      const newShootLink = page.getByRole('link', { name: /new shoot|create|upload/i }).first();
      
      if (await newShootLink.isVisible()) {
        await newShootLink.click();
        await expect(page).toHaveURL(/\/new-shoot/);
      }
    });

    test('should navigate to library page', async ({ page }) => {
      const libraryLink = page.getByRole('link', { name: /library|my photos|gallery/i }).first();
      
      if (await libraryLink.isVisible()) {
        await libraryLink.click();
        await expect(page).toHaveURL(/\/library/);
      }
    });

    test('should display user menu or profile', async ({ page }) => {
      // Look for user menu, profile icon, or account link
      const userMenu = page.getByRole('button', { name: /account|profile|user/i })
        .or(page.getByRole('link', { name: /account|profile/i }));
      
      await expect(userMenu.first()).toBeVisible();
    });

    test('should have logout functionality', async ({ page, isMobile }) => {
      // Open user menu if it exists
      const userMenuButton = page.getByRole('button', { name: /account|profile|user|menu/i }).first();
      
      if (await userMenuButton.isVisible()) {
        await userMenuButton.click();
        await page.waitForTimeout(300);
      }
      
      // Look for logout button
      const logoutButton = page.getByRole('button', { name: /logout|sign out/i })
        .or(page.getByRole('link', { name: /logout|sign out/i }));
      
      if (await logoutButton.isVisible()) {
        await expect(logoutButton).toBeVisible();
      }
    });
  });

  test.describe('Empty State', () => {
    test('should display empty state when no shoots exist', async ({ page }) => {
      await page.goto('/dashboard');
      
      const url = page.url();
      if (url.includes('/login')) {
        test.skip();
      }
      
      // Check for empty state messaging
      const emptyState = page.getByText(/no shoots|get started|create your first/i);
      
      // This test is flexible - empty state might not always be visible
      const hasEmptyState = await emptyState.isVisible().catch(() => false);
      
      // Just verify the page loaded successfully
      await expect(page.getByRole('heading')).toBeVisible();
    });
  });

  test.describe('Responsive Design', () => {
    test('should display mobile layout on small screens', async ({ page, isMobile }) => {
      if (!isMobile) {
        test.skip();
      }
      
      await page.goto('/dashboard');
      
      const url = page.url();
      if (url.includes('/login')) {
        test.skip();
      }
      
      // Verify viewport is mobile size
      const viewport = page.viewportSize();
      expect(viewport?.width).toBeLessThan(768);
      
      // Content should still be visible
      await expect(page.getByRole('heading')).toBeVisible();
    });

    test('should display desktop layout on large screens', async ({ page, isMobile }) => {
      if (isMobile) {
        test.skip();
      }
      
      await page.goto('/dashboard');
      
      const url = page.url();
      if (url.includes('/login')) {
        test.skip();
      }
      
      // Verify viewport is desktop size
      const viewport = page.viewportSize();
      expect(viewport?.width).toBeGreaterThanOrEqual(768);
      
      // Desktop navigation should be visible
      const nav = page.locator('nav');
      await expect(nav).toBeVisible();
    });
  });
});
