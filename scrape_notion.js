const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Read required environment variables
  const prefix = process.env.STREAM_PREFIX;
  const url = process.env.NOTION_PAGE_URL;

  // Validate environment variables
  if (!prefix) {
    console.error("❌ ERROR: STREAM_PREFIX environment variable is not set! Must be 'DEEN' or 'DUNYA'");
    await browser.close();
    process.exit(1);
  }

  if (!url) {
    console.error(`❌ ERROR: NOTION_PAGE_URL environment variable is not set for stream ${prefix}!`);
    await browser.close();
    process.exit(1);
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

  const outputFile = `notion_${prefix}.txt`;
  fs.writeFileSync(outputFile, final);
  console.log(`✅ ${prefix} stream: Notion content scraped and cleaned -> ${outputFile}`);
  await browser.close();
})();
