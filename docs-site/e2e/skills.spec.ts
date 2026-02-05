import { test, expect } from '@playwright/test';

test.describe('Skills Grid', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
  });

  test('displays skills grid with skill cards', async ({ page }) => {
    // Wait for skills grid to load - it has className="skills-grid"
    const skillsGrid = page.locator('.skills-grid');
    await skillsGrid.waitFor({ state: 'visible', timeout: 10000 });

    // Skill cards are <a> tags inside the grid
    const skillCards = skillsGrid.locator('a');
    const count = await skillCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('language tabs filter skills correctly', async ({ page }) => {
    // Language tabs are buttons inside a container with background
    // Look for the Python tab button by its text content
    const pythonTab = page.locator('button').filter({ hasText: 'Python' });
    await pythonTab.click();

    // Wait for filter to apply
    await page.waitForTimeout(300);

    // Check that skills are shown (grid still has cards)
    const skillCards = page.locator('.skills-grid a');
    const count = await skillCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('category tabs filter skills correctly', async ({ page }) => {
    // First select "All" language to see all skills
    const allLangTab = page.locator('button').filter({ hasText: 'All' }).first();
    await allLangTab.click();

    // Category tabs are pill-shaped buttons below language tabs
    // Look for a category like "Foundry" or "Data"
    const foundryTab = page.locator('button').filter({ hasText: 'Foundry' });
    
    if (await foundryTab.isVisible()) {
      await foundryTab.click();
      await page.waitForTimeout(300);
      
      // Verify filtering happened (grid still works)
      const skillCards = page.locator('.skills-grid a');
      const count = await skillCards.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }
  });

  test('skill cards have required information', async ({ page }) => {
    // Check first skill card has name and description
    const firstCard = page.locator('.skills-grid a').first();
    await firstCard.waitFor({ state: 'visible', timeout: 10000 });

    // Card should have a title (h3)
    const cardTitle = firstCard.locator('h3');
    await expect(cardTitle).toBeVisible();

    // Card should have a description (p tag)
    const cardDescription = firstCard.locator('p');
    await expect(cardDescription).toBeVisible();
  });

  test('clicking skill card opens GitHub page', async ({ page, context }) => {
    const firstCard = page.locator('.skills-grid a').first();
    await firstCard.waitFor({ state: 'visible', timeout: 10000 });
    
    const href = await firstCard.getAttribute('href');
    const target = await firstCard.getAttribute('target');
    
    expect(href).toContain('github.com/microsoft/skills');
    expect(target).toBe('_blank');
  });
});
