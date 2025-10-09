import { test as setup, expect } from '@playwright/test';
import path from 'path';

// Storage state paths
const authDir = path.join(__dirname, '../../playwright/.auth');
const loggedOutFile = path.join(authDir, 'logged-out.json');
const basicUserFile = path.join(authDir, 'basic-user.json');
const premiumUserFile = path.join(authDir, 'premium-user.json');

/**
 * Setup for logged-out state (guest user)
 * This creates an empty storage state
 */
setup('logged-out state', async ({ page, context }) => {
  // Just ensure we're on the landing page with no auth
  await page.goto('/');
  await expect(page).toHaveURL('/');
  
  // Save empty storage state
  await context.storageState({ path: loggedOutFile });
});

/**
 * Setup for basic authenticated user
 * This assumes you have test credentials configured
 */
setup('basic user login', async ({ page, context }) => {
  const email = process.env.TEST_USER_EMAIL || 'test@example.com';
  const password = process.env.TEST_USER_PASSWORD || 'testpassword123';
  
  await page.goto('/login');
  
  // Fill in login form
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole('button', { name: /sign in|login/i }).click();
  
  // Wait for successful navigation to dashboard
  await page.waitForURL('/dashboard', { timeout: 10000 });
  
  // Verify we're logged in
  await expect(page.getByText(/dashboard/i)).toBeVisible();
  
  // Save authenticated state
  await context.storageState({ path: basicUserFile });
});

/**
 * Setup for premium user
 * This assumes you have premium test credentials configured
 */
setup('premium user login', async ({ page, context }) => {
  const email = process.env.TEST_PREMIUM_EMAIL || 'premium@example.com';
  const password = process.env.TEST_PREMIUM_PASSWORD || 'premiumpass123';
  
  await page.goto('/login');
  
  // Fill in login form
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole('button', { name: /sign in|login/i }).click();
  
  // Wait for successful navigation
  await page.waitForURL('/dashboard', { timeout: 10000 });
  
  // Verify premium features are accessible
  await expect(page.getByText(/dashboard/i)).toBeVisible();
  
  // Save authenticated state
  await context.storageState({ path: premiumUserFile });
});
