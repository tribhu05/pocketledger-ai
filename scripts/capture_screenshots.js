const path = require('path');
const fs = require('fs');
const { chromium } = require(path.resolve(__dirname, '..', 'frontend', 'node_modules', 'playwright-core'));

async function capture() {
  const outputDir = path.resolve(__dirname, '..', 'docs', 'screenshots');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2, // 2x crisp high-res screenshot
  });

  const page = await context.newPage();

  console.log('Navigating to PocketLedger AI...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // 1. Dashboard
  console.log('Capturing Dashboard...');
  await page.screenshot({ path: path.join(outputDir, '01_dashboard.png') });

  // 2. Document Inbox
  console.log('Capturing Inbox...');
  const inboxTab = page.locator('button:has-text("Document Inbox"), a:has-text("Document Inbox"), nav button:nth-child(2)');
  if (await inboxTab.count() > 0) {
    await inboxTab.first().click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(outputDir, '02_inbox.png') });
  }

  // 3. Expense Ledger
  console.log('Capturing Ledger...');
  const ledgerTab = page.locator('button:has-text("Expense Ledger"), a:has-text("Expense Ledger"), nav button:nth-child(3)');
  if (await ledgerTab.count() > 0) {
    await ledgerTab.first().click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(outputDir, '03_ledger.png') });

    // Open Review Modal on first reviewable document
    const reviewBtn = page.locator('button:has-text("Review"), button:has-text("Edit"), table button').first();
    if (await reviewBtn.count() > 0) {
      console.log('Opening Review Modal...');
      await reviewBtn.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: path.join(outputDir, '04_review_modal.png') });
      
      // Reload page to return to clean state
      await page.reload({ waitUntil: 'networkidle' });
      await page.waitForTimeout(1000);
    }
  }

  // 4. Reports & CSV
  console.log('Capturing Reports...');
  const reportsTab = page.locator('button:has-text("Reports"), a:has-text("Reports")');
  if (await reportsTab.count() > 0) {
    await reportsTab.first().click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(outputDir, '05_reports_csv.png') });
  }

  // 5. Settings / Privacy
  console.log('Capturing Privacy & System Status...');
  const settingsTab = page.locator('button:has-text("Privacy"), button:has-text("Settings"), a:has-text("Privacy")');
  if (await settingsTab.count() > 0) {
    await settingsTab.first().click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(outputDir, '06_system_status.png') });
  }

  await browser.close();
  console.log('All screenshots captured successfully in', outputDir);
}

capture().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
