# Playwright Testing Documentation

## Overview

This project uses [Playwright](https://playwright.dev/) for end-to-end testing across multiple browsers, devices, and viewports.

## Test Matrix Coverage

We test the webapp across **10 device/browser combinations** to ensure comprehensive coverage:

### Desktop Browsers
1. **Chrome on Windows 11** (1920×1080) - Light theme - Logged-out
2. **Chrome on macOS** (1440×900) - Dark theme - Premium user
3. **Firefox on macOS** (1280×800) - Light theme - Basic user
4. **Safari (WebKit) on macOS** (1440×900) - Light theme
5. **Safari (WebKit) on macOS** (1440×900) - Dark theme - Long data

### Mobile Devices
6. **iPhone 14 Pro** (Safari) - Light theme - Basic user
7. **iPhone 14 Pro** (Safari) - Dark theme - Empty data
8. **Pixel 7** (Chrome) - Light theme - Premium user

### Tablet Devices
9. **iPad Pro 11** (Safari) - Light theme - Basic user
10. **Galaxy Tab S4** (Chrome) - Dark theme - Logged-out

## Setup

### Prerequisites
- Node.js 18+ installed
- Project dependencies installed (`npm install`)
- Playwright browsers installed (`npx playwright install`)

### Environment Variables

Create a `.env.test` file in the frontend directory with test credentials:

```env
# Test user credentials
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpassword123

# Premium test user
TEST_PREMIUM_EMAIL=premium@example.com
TEST_PREMIUM_PASSWORD=premiumpass123

# Base URL (optional, defaults to http://localhost:5173)
BASE_URL=http://localhost:5173
```

## Running Tests

### All Tests
```bash
npm test
```

### Interactive UI Mode
```bash
npm run test:ui
```
This opens the Playwright Test UI for debugging and watching tests run in real-time.

### Headed Mode (See Browser)
```bash
npm run test:headed
```

### Specific Browser
```bash
npm run test:chromium  # Chrome/Chromium tests
npm run test:firefox   # Firefox tests
npm run test:webkit    # Safari/WebKit tests
```

### Specific Device Type
```bash
npm run test:mobile    # iPhone + Pixel tests
npm run test:tablet    # iPad + Galaxy Tab tests
```

### Debug Mode
```bash
npm run test:debug
```
Opens tests in debug mode with the Playwright Inspector.

### View Test Report
```bash
npm run test:report
```
Opens the HTML test report in your browser.

## Test Structure

```
frontend/
├── tests/
│   ├── auth/
│   │   └── auth.setup.ts          # Authentication state setup
│   ├── fixtures/
│   │   └── auth-fixtures.ts       # Custom test fixtures
│   ├── utils/
│   │   └── test-helpers.ts        # Reusable test utilities
│   ├── landing.spec.ts            # Landing page tests
│   ├── authentication.spec.ts     # Login/register tests
│   └── dashboard.spec.ts          # Dashboard tests
├── playwright/
│   └── .auth/                     # Stored auth states
└── playwright.config.ts           # Playwright configuration
```

## Test Scenarios Covered

### 1. Landing Page (`landing.spec.ts`)
- ✅ Display key elements (heading, CTA, login link)
- ✅ Navigation to login page
- ✅ Navigation to register page
- ✅ Responsive mobile layout
- ✅ Proper metadata (title, description)

### 2. Authentication (`authentication.spec.ts`)
- ✅ Login form display and validation
- ✅ Registration form display and validation
- ✅ Google OAuth button presence
- ✅ Error handling for invalid credentials
- ✅ Email format validation
- ✅ Protected route redirects

### 3. Dashboard (`dashboard.spec.ts`)
- ✅ Dashboard heading and navigation
- ✅ Navigation between protected pages
- ✅ User menu and logout functionality
- ✅ Empty state display
- ✅ Responsive layouts (mobile vs desktop)

### 4. User States
- **Logged-out**: Landing page, login, register
- **Basic User**: Dashboard, library, new shoot
- **Premium User**: All features + premium-only content

### 5. Themes
- **Light theme**: Default color scheme
- **Dark theme**: Dark mode color scheme

### 6. Data States
- **Empty**: No shoots/content
- **Long data**: Multiple shoots/items

## Writing New Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/your-page');
  });

  test('should do something', async ({ page }) => {
    // Test code here
    await expect(page.getByRole('button')).toBeVisible();
  });
});
```

### Using Test Helpers

```typescript
import { 
  fillFormField, 
  isAuthenticated, 
  waitForPageLoad 
} from './utils/test-helpers';

test('example test', async ({ page }) => {
  await page.goto('/login');
  await fillFormField(page, /email/i, 'test@example.com');
  await fillFormField(page, /password/i, 'password123');
  
  const authenticated = await isAuthenticated(page);
  expect(authenticated).toBeTruthy();
});
```

### Testing Responsive Layouts

```typescript
test('should work on mobile', async ({ page, isMobile }) => {
  if (!isMobile) {
    test.skip(); // Skip on desktop
  }
  
  const viewport = page.viewportSize();
  expect(viewport?.width).toBeLessThan(768);
});
```

## Best Practices

### 1. Use Semantic Selectors
```typescript
// ✅ Good - semantic, resilient
await page.getByRole('button', { name: /submit/i });
await page.getByLabel(/email/i);

// ❌ Bad - brittle, implementation-specific
await page.locator('.btn-submit');
await page.locator('#email-input');
```

### 2. Wait for Elements Properly
```typescript
// ✅ Good - explicit wait
await expect(page.getByText('Success')).toBeVisible();

// ❌ Bad - arbitrary timeout
await page.waitForTimeout(3000);
```

### 3. Test User Flows, Not Implementation
```typescript
// ✅ Good - tests the flow
test('user can create a new shoot', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByRole('button', { name: /new shoot/i }).click();
  await page.getByLabel(/title/i).fill('My Shoot');
  await page.getByRole('button', { name: /create/i }).click();
  await expect(page.getByText('Shoot created')).toBeVisible();
});

// ❌ Bad - tests implementation details
test('button has correct class', async ({ page }) => {
  const button = page.locator('.btn-primary');
  expect(await button.getAttribute('class')).toContain('bg-blue-500');
});
```

### 4. Keep Tests Independent
Each test should be able to run in isolation without depending on other tests.

```typescript
// ✅ Good - independent
test.beforeEach(async ({ page }) => {
  await page.goto('/dashboard');
  // Set up fresh state for each test
});

// ❌ Bad - dependent
test('create shoot', async ({ page }) => { /* ... */ });
test('edit shoot', async ({ page }) => { 
  // Assumes previous test ran
});
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Playwright Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - name: Install dependencies
        run: npm ci
        working-directory: ./frontend
      - name: Install Playwright Browsers
        run: npx playwright install --with-deps
        working-directory: ./frontend
      - name: Run Playwright tests
        run: npm test
        working-directory: ./frontend
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## Debugging

### Debug a Specific Test
```bash
npx playwright test authentication.spec.ts --debug
```

### View Trace Files
If a test fails, Playwright generates trace files. View them with:
```bash
npx playwright show-trace path/to/trace.zip
```

### Screenshots and Videos
Failed tests automatically capture:
- Screenshots (`test-results/`)
- Videos (if configured)
- Traces (on retry)

### Playwright Inspector
Use `await page.pause()` in your test to open the Inspector:
```typescript
test('debug this', async ({ page }) => {
  await page.goto('/dashboard');
  await page.pause(); // Opens Inspector
});
```

## Continuous Improvement

### Adding New Test Scenarios
1. Identify critical user flows
2. Add test file to `tests/` directory
3. Follow naming convention: `feature-name.spec.ts`
4. Update this documentation

### Expanding Coverage
- Add more device combinations as needed
- Test edge cases (slow networks, offline mode)
- Add visual regression testing
- Test accessibility (a11y)

## Troubleshooting

### Tests Fail Locally But Pass in CI
- Check for timing issues (increase timeouts)
- Verify environment variables are set
- Ensure dev server is running

### Flaky Tests
- Use `test.retry(2)` for flaky tests
- Add explicit waits instead of `waitForTimeout`
- Check for race conditions

### Browser Not Found
```bash
npx playwright install
```

## Resources

- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-playwright)
- [Debugging Guide](https://playwright.dev/docs/debug)
