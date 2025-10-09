import { defineConfig, devices } from '@playwright/test';

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  testDir: './tests',
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: process.env.CI ? 'github' : 'html',
  
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.BASE_URL || 'http://localhost:5173',
    
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    
    /* Screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Video on failure */
    video: 'retain-on-failure',
  },

  /* Configure projects for major browsers and devices */
  projects: [
    // Setup project for authentication states
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },

    // Desktop browsers - Light theme
    {
      name: 'chromium-desktop-light',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
        colorScheme: 'light',
      },
      dependencies: ['setup'],
    },
    
    {
      name: 'firefox-desktop-light',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1280, height: 800 },
        colorScheme: 'light',
      },
      dependencies: ['setup'],
    },
    
    {
      name: 'webkit-desktop-light',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1440, height: 900 },
        colorScheme: 'light',
      },
      dependencies: ['setup'],
    },

    // Desktop browsers - Dark theme
    {
      name: 'chromium-desktop-dark',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1440, height: 900 },
        colorScheme: 'dark',
      },
      dependencies: ['setup'],
    },

    {
      name: 'webkit-desktop-dark',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1440, height: 900 },
        colorScheme: 'dark',
      },
      dependencies: ['setup'],
    },

    // Mobile devices
    {
      name: 'mobile-iphone-light',
      use: { 
        ...devices['iPhone 14 Pro'],
        colorScheme: 'light',
      },
      dependencies: ['setup'],
    },

    {
      name: 'mobile-iphone-dark',
      use: { 
        ...devices['iPhone 14 Pro'],
        colorScheme: 'dark',
      },
      dependencies: ['setup'],
    },

    {
      name: 'mobile-pixel-light',
      use: { 
        ...devices['Pixel 7'],
        colorScheme: 'light',
      },
      dependencies: ['setup'],
    },

    // Tablet devices
    {
      name: 'tablet-ipad-light',
      use: { 
        ...devices['iPad Pro 11'],
        colorScheme: 'light',
      },
      dependencies: ['setup'],
    },

    {
      name: 'tablet-galaxy-dark',
      use: {
        ...devices['Galaxy Tab S4'],
        colorScheme: 'dark',
      },
      dependencies: ['setup'],
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    stdout: 'ignore',
    stderr: 'pipe',
  },
});
