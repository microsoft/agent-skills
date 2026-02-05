import { test, expect } from '@playwright/test';

test.describe('Command Palette Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await page.waitForLoadState('networkidle');
  });

  test('opens command palette with Cmd+K (Mac) or Ctrl+K (Windows/Linux)', async ({ page }) => {
    await page.keyboard.press('Control+k');

    const commandPalette = page.locator('[cmdk-root]');
    await expect(commandPalette).toBeVisible({ timeout: 5000 });
  });

  test('search input receives focus when palette opens', async ({ page }) => {
    await page.keyboard.press('Control+k');

    const searchInput = page.locator('[cmdk-input]');
    await expect(searchInput).toBeVisible({ timeout: 5000 });
    await expect(searchInput).toBeFocused();
  });

  test('typing in search filters results', async ({ page }) => {
    await page.keyboard.press('Control+k');

    const searchInput = page.locator('[cmdk-input]');
    await expect(searchInput).toBeVisible({ timeout: 5000 });
    await searchInput.fill('cosmos');

    await page.waitForTimeout(300);

    const results = page.locator('[cmdk-item]');
    await expect(results.first()).toBeVisible({ timeout: 5000 });
  });

  test('closes command palette with Escape key', async ({ page }) => {
    await page.keyboard.press('Control+k');

    const commandPalette = page.locator('[cmdk-root]');
    await expect(commandPalette).toBeVisible({ timeout: 5000 });

    await page.keyboard.press('Escape');

    await expect(commandPalette).not.toBeVisible();
  });

  test('clicking search button opens command palette', async ({ page }) => {
    const searchButton = page.locator('button:has-text("Search skills...")');
    await expect(searchButton).toBeVisible({ timeout: 5000 });
    await searchButton.click();

    const commandPalette = page.locator('[cmdk-root]');
    await expect(commandPalette).toBeVisible({ timeout: 5000 });
  });
});
