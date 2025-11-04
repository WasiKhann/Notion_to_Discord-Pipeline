 # 🌙 Private Motion Pipeline

A dual-stream automation system that scrapes content from two different Notion pages (Deen and Dunya) and delivers curated snippets to separate Discord channels.

## 🔄 Workflow Overview

The pipeline processes two independent streams:
1. **Deen Stream**: Religious/spiritual content
2. **Dunya Stream**: Worldly/general content

Each stream:
- Scrapes a dedicated Notion page
- Processes and filters the content
- Sends curated snippets to a specific Discord channel
- Maintains its own history to avoid recent repeats

## 🛠️ Technical Components

### 1. Content Scraping (`scrape_notion.js`)
- Uses Playwright for headless browser automation
- Handles stream-specific Notion page URLs
- Cleans and formats content into `notion_[STREAM].txt` files
- Validates required environment variables

### 2. Snippet Processing (`send_notification.py`)
- Processes stream-specific content files
- Implements smart snippet selection:
  - Categories: "Allah says" and "Knowing Allah" snippets
  - Maintains selection history
  - Avoids recent repeats (7-day window)
  - Alternates between categories
- Handles message chunking for Discord's character limits
- Tracks sent snippets in `sent_snippets_[STREAM].json`

### 3. Workflow Automation (`scrape.yml`)
- Runs daily via GitHub Actions
- Sequential stream processing (Deen → Dunya)
- Stream-specific environment variables and secrets
- Automated history file management

## 🔧 Configuration

### Required Secrets
- `NOTION_PAGE_URL_DEEN`: URL for the Deen stream Notion page
- `NOTION_PAGE_URL_DUNYA`: URL for the Dunya stream Notion page
- `DISCORD_WEBHOOK_URL_DEEN`: Discord webhook for Deen content
- `DISCORD_WEBHOOK_URL_DUNYA`: Discord webhook for Dunya content

### Key Settings (`send_notification.py`)
- `RECENCY_DAYS`: Days before snippets can repeat (default: 7)
- `NUM_SNIPPETS`: Snippets to send per day (default: 10)
- `DISCORD_CHAR_LIMIT`: Safe character limit for Discord messages

## 📋 File Structure
```
.
├── .github/workflows/
│   └── scrape.yml          # GitHub Actions workflow
├── scrape_notion.js        # Notion content scraper
├── send_notification.py    # Snippet processor and sender
├── notion_DEEN.txt        # Scraped Deen content
├── notion_DUNYA.txt       # Scraped Dunya content
├── sent_snippets_DEEN.json  # Deen stream history
└── sent_snippets_DUNYA.json # Dunya stream history
```

## 🚀 Execution Flow

1. **Deen Stream Processing**
   - Scrapes Deen Notion page → `notion_DEEN.txt`
   - Processes and sends Deen snippets
   - Updates `sent_snippets_DEEN.json`

2. **Dunya Stream Processing**
   - Scrapes Dunya Notion page → `notion_DUNYA.txt`
   - Processes and sends Dunya snippets
   - Updates `sent_snippets_DUNYA.json`

## 🔍 Debug Features
- Content verification steps for Dunya stream
- Detailed logging throughout the process
- Force-add flags for history files in git

## 📝 Content Format
Notion pages should use `..` on a new line to separate distinct snippets:
```
         First snippet content here
Multiple lines are supported
..
Second snippet content here
..
And so on
```

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License
MIT License - See LICENSE file for details

        ### Step 1: Create Your GitHub Repository and Add Files

        1.  Create a new GitHub repository (or fork this one).
        2.  Add the three core files to your repository in their respective paths:
            * `.github/workflows/scrape.yml`
            * `scrape_notion.js`
            * `send_notification.py`

        ### Step 2: Add Repository Secrets

        In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**. Click **"New repository secret"** and add the following secrets, using the exact names as shown:

        * `NOTION_PAGE_URL` (This is the URL of your Notion page)
        * `DISCORD_WEBHOOK_URL`

        ### Step 3: Update Project Files

        Navigate to each file in your repository and update its content as described below.

        1.  **`.github/workflows/scrape.yml`:**
            * Ensure the `cron` schedule is set to your desired time (currently `0 6 * * *` for 6:00 AM UTC daily).
            * Verify that `NOTION_PAGE_URL` is passed as an environment variable to the `Scrape Notion page` step.
            * Confirm the `DISCORD_WEBHOOK_URL` secret is passed to the `Send notification` step.
            * See the latest version of this file in your repository: [`./.github/workflows/scrape.yml`](./.github/workflows/scrape.yml)

        2.  **`scrape_notion.js`:**
            * Modify the `url` constant to read from the environment variable `NOTION_URL` (this variable is set in `.github/workflows/scrape.yml`).
            * Adjust the `filter` logic if your Notion page title or "Get Notion free" text varies from the defaults.
            * See the latest version of this file in your repository: [`./scrape_notion.js`](./scrape_notion.js)

        3.  **`send_notification.py`:**
            * Verify `NUM_SNIPPETS` is set to your desired number of snippets to include in the notification.
            * See the latest version of this file in your repository: [`./send_notification.py`](./send_notification.py)

        ### Step 4: Run and Verify

        * Commit all your changes to your GitHub repository.
        * Go to the "Actions" tab in your repository.
        * Select the "Daily Notion Reminder" workflow.
        * Click "Run workflow" (on the right side) to trigger a manual run and test your setup immediately.
        * Check your Discord channel for the reminders. Review the workflow logs for any errors.

        ---

        ## Contributing (Optional)

        If you'd like to improve this project:

        1.  Fork the repository.
        2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
        3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
        4.  Push to the branch (`git push origin feature/AmazingFeature`).
        5.  Open a Pull Request.

        ## License

        Distributed under the MIT License. See `LICENSE` for more information. (You might want to create a `LICENSE` file in your repo).

        ## Contact

        Wasi Khan - [LinkedIn](https://www.linkedin.com/in/wasi-khann/) - wasitahirkhan@gmail.com

        Project Link: [Daily Islamic Reminder Automation](https://github.com/WasiKhann/Daily-Islamic-Reminder-Automation)

        ````
