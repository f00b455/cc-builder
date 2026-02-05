import { test, expect, _electron as electron } from '@playwright/test';
import type { ElectronApplication, Page } from '@playwright/test';

let electronApp: ElectronApplication;
let window: Page;

test.beforeAll(async () => {
  electronApp = await electron.launch({ args: ['.'] });
  window = await electronApp.firstWindow();
});

test.afterAll(async () => {
  await electronApp.close();
});

test('app window opens', async () => {
  const title = await window.title();
  expect(title).toBeTruthy();
});

test('no console errors on startup', async () => {
  const errors: string[] = [];
  window.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  await window.reload();
  await window.waitForLoadState('domcontentloaded');

  expect(errors).toHaveLength(0);
});
