const path = require('path');
const fs = require('fs');
const { chromium } = require(path.resolve(__dirname, '..', 'frontend', 'node_modules', 'playwright-core'));

async function capture() {
  const outputDir = path.resolve(__dirname, '..', 'docs', 'screenshots');
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 600, height: 900 },
    deviceScaleFactor: 2,
  });

  const page = await context.newPage();
  const htmlPath = 'file:///' + path.resolve(__dirname, 'whatsapp_mock.html').replace(/\\/g, '/');

  console.log('Loading WhatsApp mock from:', htmlPath);
  await page.goto(htmlPath);
  await page.waitForTimeout(500);

  const phone = page.locator('.phone-container');
  const destPath = path.join(outputDir, 'whatsapp_feedback.png');

  await phone.screenshot({ path: destPath });
  console.log('WhatsApp feedback screenshot saved to:', destPath);

  await browser.close();
}

capture().catch(err => {
  console.error(err);
  process.exit(1);
});
