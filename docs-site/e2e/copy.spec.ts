import { test, expect } from '@playwright/test';

test.describe('Copy to Clipboard', () => {
  test.beforeEach(async ({ page, context }) => {
    await context.grantPermissions(['clipboard-read', 'clipboard-write']);
    await page.goto('./');
    await page.waitForLoadState('networkidle');
  });

  test('copy button is visible on skill cards', async ({ page }) => {
    const skillCard = page.locator('.skills-grid a').first();
    await skillCard.waitFor({ state: 'visible', timeout: 10000 });

    await skillCard.hover();

    const copyButton = skillCard.locator('button:has-text("Copy")');
    await expect(copyButton).toBeVisible();
  });

  test('clicking copy button shows success feedback', async ({ page }) => {
    const skillCard = page.locator('.skills-grid a').first();
    await skillCard.waitFor({ state: 'visible', timeout: 10000 });
    await skillCard.hover();

    const copyButton = skillCard.locator('button:has-text("Copy")');
    await expect(copyButton).toBeVisible();
    await copyButton.click();

    const copiedButton = skillCard.locator('button:has-text("Copied!")');
    await expect(copiedButton).toBeVisible({ timeout: 3000 });
  });

  test('copy button copies correct install command', async ({ page }) => {
    const skillCard = page.locator('.skills-grid a').first();
    await skillCard.waitFor({ state: 'visible', timeout: 10000 });
    await skillCard.hover();

    const copyButton = skillCard.locator('button:has-text("Copy")');
    await expect(copyButton).toBeVisible();
    await copyButton.click();

    const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
    
    expect(clipboardText).toMatch(/npx skills add microsoft\/skills --skill/);
  });
});
