import { test, expect } from '@playwright/test';
import { fillFormField, hasErrorMessage, isAuthenticated } from './utils/test-helpers';

test.describe('Authentication', () => {
  
  test.describe('Login', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/login');
    });

    test('should display login form', async ({ page }) => {
      await expect(page.getByRole('heading', { name: /login/i })).toBeVisible();
      await expect(page.locator('input[type="email"]')).toBeVisible();
      await expect(page.locator('input[type="password"]')).toBeVisible();
      await expect(page.getByRole('button', { name: /login/i })).toBeVisible();
    });

    test('should show validation errors for empty fields', async ({ page }) => {
      await page.getByRole('button', { name: /sign in|login/i }).click();
      
      // Wait a moment for validation to trigger
      await page.waitForTimeout(500);
      
      // Check for validation messages (may be HTML5 validation or custom)
      const emailInput = page.getByLabel(/email/i);
      const passwordInput = page.getByLabel(/password/i);
      
      // HTML5 validation check
      const emailValid = await emailInput.evaluate((el: HTMLInputElement) => el.validity.valid);
      expect(emailValid).toBeFalsy();
    });

    test('should show error for invalid credentials', async ({ page }) => {
      await fillFormField(page, /email/i, 'invalid@example.com');
      await fillFormField(page, /password/i, 'wrongpassword');
      await page.getByRole('button', { name: /sign in|login/i }).click();
      
      // Wait for error message
      await page.waitForTimeout(1000);
      
      // Check for error (this will depend on your actual implementation)
      const hasError = await hasErrorMessage(page);
      expect(hasError).toBeTruthy();
    });

    test('should display Google OAuth button', async ({ page }) => {
      const googleButton = page.getByRole('button', { name: /google|continue with google/i })
        .or(page.getByRole('link', { name: /google|continue with google/i }));
      await expect(googleButton).toBeVisible();
    });

    test('should have link to register page', async ({ page }) => {
      const registerLink = page.getByRole('link', { name: /sign up|register|create account/i });
      await expect(registerLink).toBeVisible();
      
      await registerLink.click();
      await expect(page).toHaveURL(/\/(register|signup)/);
    });
  });

  test.describe('Register', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/register');
    });

    test('should display registration form', async ({ page }) => {
      await expect(page.getByRole('heading', { name: /sign up|register|create account/i })).toBeVisible();
      await expect(page.getByLabel(/email/i)).toBeVisible();
      await expect(page.getByLabel(/password/i)).toBeVisible();
    });

    test('should show validation errors for empty fields', async ({ page }) => {
      await page.getByRole('button', { name: /sign up|register|create account/i }).click();
      
      await page.waitForTimeout(500);
      
      const emailInput = page.getByLabel(/email/i);
      const emailValid = await emailInput.evaluate((el: HTMLInputElement) => el.validity.valid);
      expect(emailValid).toBeFalsy();
    });

    test('should validate email format', async ({ page }) => {
      await fillFormField(page, /email/i, 'notanemail');
      
      const emailInput = page.getByLabel(/email/i);
      const emailValid = await emailInput.evaluate((el: HTMLInputElement) => el.validity.valid);
      expect(emailValid).toBeFalsy();
    });

    test('should have link to login page', async ({ page }) => {
      const loginLink = page.getByRole('link', { name: /sign in|login|already have account/i });
      await expect(loginLink).toBeVisible();
      
      await loginLink.click();
      await expect(page).toHaveURL(/\/login/);
    });
  });

  test.describe('Protected Routes', () => {
    test('should redirect to login when accessing dashboard without auth', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Should be redirected to login
      await page.waitForURL(/\/login/, { timeout: 5000 });
      await expect(page).toHaveURL(/\/login/);
    });

    test('should redirect to login when accessing library without auth', async ({ page }) => {
      await page.goto('/library');
      await page.waitForURL(/\/login/, { timeout: 5000 });
      await expect(page).toHaveURL(/\/login/);
    });

    test('should redirect to login when accessing new-shoot without auth', async ({ page }) => {
      await page.goto('/new-shoot');
      await page.waitForURL(/\/login/, { timeout: 5000 });
      await expect(page).toHaveURL(/\/login/);
    });
  });
});
