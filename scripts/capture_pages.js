const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  // Set auth state
  await page.goto('http://localhost:6019/login');
  await page.evaluate(() => {
    localStorage.setItem('token', 'demo-token');
    localStorage.setItem('role', 'admin');
    localStorage.setItem('user_name', 'Demo Admin');
  });

  // Navigate to admins page
  await page.goto('http://localhost:6019/educational/admins');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'ux-screenshots/admins_authenticated.png', fullPage: true });

  // Navigate to instructors page
  await page.goto('http://localhost:6019/educational/instructors');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'ux-screenshots/instructors_authenticated.png', fullPage: true });

  await browser.close();
  console.log('Screenshots captured successfully!');
})();
