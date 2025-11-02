const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Read the URL from environment variable
  const url = process.env.NOTION_PAGE_URL; // <--- CHANGE THIS LINE

  if (!url) { // <--- Optional: Add a check to ensure the URL is present
    console.error("❌ ERROR: NOTION_PAGE_URL environment variable is not set!");
    await browser.close();
    process.exit(1); // Exit with an error code
  }

  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(5000); // Let Notion fully render

  // Grab content with original line breaks preserved
  const content = await page.evaluate(() => {
    return document.querySelector('main')?.innerText || document.body.innerText;
  });

  // Remove first few lines (title and "Get Notion free")
  const lines = content.split('\n');
  const cleaned = lines.filter(line => (
    !line.includes('Most imp Notion page') && !line.includes('Get Notion free')
  )).join('\n');

  // Re-inject clean spacing around marker
  const final = cleaned.replace(/\n?\.\.\n?/g, '\n..\n');

  fs.writeFileSync('notion.txt', final);
  console.log("✅ Notion content scraped and cleaned.");
  await browser.close();
})();
