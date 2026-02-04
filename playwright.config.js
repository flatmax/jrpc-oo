import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/playwright',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'https://0.0.0.0:8081',
    trace: 'on-first-retry',
    ignoreHTTPSErrors: true, // Required for self-signed certs
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run start:no_wss',
    url: 'https://0.0.0.0:8081',
    reuseExistingServer: !process.env.CI,
    ignoreHTTPSErrors: true,
  },
});
