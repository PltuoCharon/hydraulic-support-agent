import { test, expect } from '@playwright/test'

test('push jack design works through real browser and API', async ({ page }) => {
  await page.goto('/#/calc?m=jack')

  const push = page.getByTestId('jack-push-required').locator('input')
  const pressure = page.getByTestId('jack-pressure').locator('input')

  await push.fill('300')
  await pressure.fill('31.5')

  await page.getByTestId('jack-calculate').click()

  await expect(page.getByTestId('jack-result')).toBeVisible()
  await expect(page.getByTestId('jack-bore-candidate')).toHaveText('125')
  await expect(page.getByTestId('jack-push-check')).toContainText('满足')

  await push.fill('350')

  await expect(page.getByTestId('jack-result')).toHaveCount(0)
})
