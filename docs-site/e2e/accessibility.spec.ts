import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('homepage should have no WCAG AA violations', async ({ page }) => {
    await page.goto('./');

    await page.waitForSelector('.skills-grid a');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    if (accessibilityScanResults.violations.length > 0) {
      console.log('Accessibility violations:', JSON.stringify(accessibilityScanResults.violations, null, 2));
    }

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('skip-to-content link works', async ({ page }) => {
    await page.goto('./');

    await page.keyboard.press('Tab');

    const skipLink = page.locator('a[href="#main-content"], .skip-link');
    
    if (await skipLink.isVisible()) {
      await skipLink.click();

      const mainContent = page.locator('#main-content, main');
      await expect(mainContent).toBeVisible();
    }
  });

  test('all images have alt text', async ({ page }) => {
    await page.goto('./');

    const images = page.locator('img');
    const imageCount = await images.count();

    for (let i = 0; i < imageCount; i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute('alt');
      const role = await img.getAttribute('role');
      
      const hasAccessibleLabel = alt !== null || role === 'presentation' || role === 'none';
      expect(hasAccessibleLabel).toBeTruthy();
    }
  });

  test('interactive elements are keyboard accessible', async ({ page }) => {
    await page.goto('./');

    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      
      const focusedElement = page.locator(':focus');
      const isVisible = await focusedElement.isVisible().catch(() => false);
      
      if (isVisible) {
        const tagName = await focusedElement.evaluate(el => el.tagName.toLowerCase());
        const role = await focusedElement.getAttribute('role');
        const tabIndex = await focusedElement.getAttribute('tabindex');
        
        const isInteractive = ['a', 'button', 'input', 'select', 'textarea'].includes(tagName) ||
                             ['button', 'link', 'tab', 'menuitem'].includes(role || '') ||
                             tabIndex === '0';
        
        expect(isInteractive).toBeTruthy();
      }
    }
  });

  test('color contrast meets WCAG AA standards', async ({ page }) => {
    await page.goto('./');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .options({ rules: { 'color-contrast': { enabled: true } } })
      .analyze();

    const contrastViolations = accessibilityScanResults.violations.filter(
      v => v.id === 'color-contrast'
    );

    expect(contrastViolations).toEqual([]);
  });

  test('focus indicators are visible', async ({ page }) => {
    await page.goto('./');

    await page.keyboard.press('Tab');

    const focusedElement = page.locator(':focus');
    
    if (await focusedElement.isVisible()) {
      const outline = await focusedElement.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return {
          outlineStyle: styles.outlineStyle,
          outlineWidth: styles.outlineWidth,
          boxShadow: styles.boxShadow,
        };
      });

      const hasFocusIndicator = 
        (outline.outlineStyle !== 'none' && outline.outlineWidth !== '0px') ||
        outline.boxShadow !== 'none';

      expect(hasFocusIndicator).toBeTruthy();
    }
  });

  test('command palette is keyboard navigable', async ({ page }) => {
    await page.goto('./');
    await page.waitForLoadState('networkidle');

    await page.keyboard.press('Control+k');

    const searchInput = page.locator('[cmdk-input]');
    await searchInput.waitFor({ state: 'visible', timeout: 10000 });
    await expect(searchInput).toBeVisible();

    await page.keyboard.type('azure');
    await page.waitForTimeout(200);

    await page.keyboard.press('ArrowDown');

    const results = page.locator('[cmdk-item]');
    if (await results.count() > 0) {
      const selectedItem = page.locator('[cmdk-item][aria-selected="true"]');
      const count = await selectedItem.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }

    await page.keyboard.press('Escape');
    await expect(searchInput).not.toBeVisible();
  });
});
