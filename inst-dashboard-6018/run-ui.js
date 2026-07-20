const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: false
  });

  const page = await browser.newPage();

  await page.goto('http://localhost:3000');

  await page.waitForTimeout(10000);

  await page.screenshot({
    path: 'ui.png',
    fullPage: true
  });

  await browser.close();

  console.log("Screenshot saved: ui.png");
})();