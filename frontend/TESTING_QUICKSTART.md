# Playwright Testing - Quick Start

## 🚀 Get Started in 3 Steps

### 1. Set Up Test Environment (One-Time)

Create `.env.test` in the `frontend/` directory:

```bash
# Test user credentials
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpassword123

# Premium test user  
TEST_PREMIUM_EMAIL=premium@example.com
TEST_PREMIUM_PASSWORD=premiumpass123
```

> **Note**: You'll need to create these test users in your database first.

### 2. Run Your First Test

```bash
cd frontend
npm run test:ui
```

This opens the interactive Playwright UI where you can:
- See all tests
- Run tests visually
- Debug failures
- Watch tests in real-time

### 3. Run All Tests

```bash
npm test
```

## 📋 Common Commands

```bash
# Interactive mode (recommended for development)
npm run test:ui

# Run all tests in all browsers
npm test

# Run tests visually (see the browser)
npm run test:headed

# Test specific browser
npm run test:chromium
npm run test:firefox  
npm run test:webkit

# Test specific devices
npm run test:mobile
npm run test:tablet

# Debug a failing test
npm run test:debug

# View test report
npm run test:report
```

## 🎯 What's Being Tested

The test suite covers **10 browser/device combinations**:

- **Desktop**: Chrome, Firefox, Safari (light & dark themes)
- **Mobile**: iPhone 14 Pro, Pixel 7
- **Tablet**: iPad Pro, Galaxy Tab

### Test Scenarios
✅ Landing page navigation  
✅ Login/registration flows  
✅ Protected route redirects  
✅ Dashboard functionality  
✅ Responsive layouts  
✅ Form validation  
✅ OAuth integration  

## 🐛 Troubleshooting

### Tests failing with "Browser not found"
```bash
npx playwright install
```

### Tests failing with "connect ECONNREFUSED"
Make sure your dev server is running:
```bash
npm run dev
```

### Want to see what's happening?
Use headed mode to watch tests run:
```bash
npm run test:headed
```

## 📚 Next Steps

For detailed documentation, see [TESTING.md](./TESTING.md)

For writing your own tests, check the examples in `tests/` directory.
