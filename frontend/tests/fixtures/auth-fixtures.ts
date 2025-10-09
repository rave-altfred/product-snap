import { test as base } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

// ES module fix for __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Storage state paths
const authDir = path.join(__dirname, '../../playwright/.auth');

type AuthFixtures = {
  loggedOutPage: void;
  basicUserPage: void;
  premiumUserPage: void;
};

/**
 * Custom fixtures that extend the base test with different authentication states
 */
export const test = base.extend<AuthFixtures>({
  /**
   * Fixture for logged-out state
   */
  loggedOutPage: async ({ context }, use) => {
    const loggedOutFile = path.join(authDir, 'logged-out.json');
    await context.addCookies([]);
    await use();
  },

  /**
   * Fixture for basic user state
   */
  basicUserPage: async ({ context }, use) => {
    const basicUserFile = path.join(authDir, 'basic-user.json');
    // Note: In actual tests, use storageState in the test config
    await use();
  },

  /**
   * Fixture for premium user state
   */
  premiumUserPage: async ({ context }, use) => {
    const premiumUserFile = path.join(authDir, 'premium-user.json');
    // Note: In actual tests, use storageState in the test config
    await use();
  },
});

export { expect } from '@playwright/test';
