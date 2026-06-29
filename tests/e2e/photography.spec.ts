import { test, expect } from '@playwright/test'

test.describe('Photography gallery', () => {
  test('renders photo cards on the gallery page', async ({ page }) => {
    await page.goto('/photography')
    await expect(page.locator('[data-testid="photo-card"]').first()).toBeVisible({
      timeout: 15_000,
    })
  })

  test('opens lightbox when a photo card is clicked', async ({ page }) => {
    await page.goto('/photography')
    await page.locator('[data-testid="photo-card"]').first().waitFor({ state: 'visible', timeout: 15_000 })
    await page.locator('[data-testid="photo-card"]').first().click()
    await expect(page.locator('[data-testid="lightbox"]')).toBeVisible()
  })

  test('closes lightbox with Escape key', async ({ page }) => {
    await page.goto('/photography')
    await page.locator('[data-testid="photo-card"]').first().waitFor({ state: 'visible', timeout: 15_000 })
    await page.locator('[data-testid="photo-card"]').first().click()
    await expect(page.locator('[data-testid="lightbox"]')).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(page.locator('[data-testid="lightbox"]')).not.toBeVisible()
  })
})
