 # 🌙 Daily Islamic Reminder Automation

## Project Overview

This project automates the process of delivering daily Islamic reminders from a Notion page directly to my email inbox and Telegram chat. Leveraging GitHub Actions for scheduled execution, Node.js with Playwright for web scraping, and Python for data parsing and multi-platform notification delivery, this solution ensures I receive curated spiritual content consistently.

This project demonstrates practical skills in:
* **Web Scraping:** Using Playwright to extract dynamic content from Notion web page.
* **Workflow Automation:** Orchestrating a multi-step process with GitHub Actions for reliable scheduling.
* **Cross-Platform Notification:** Sending personalized messages via Email (SMTP) and Telegram Bot API.
* **Data Parsing & Manipulation:** Extracting and structuring text data from raw scraped content.
* **Secure Credential Management:** Utilizing GitHub Secrets for sensitive API keys and login details.
* **Version Control & Documentation:** Maintaining a clear and reproducible project setup.

---

## How It Works

1.  **Notion Scraping (`scrape_notion.js`):** A Node.js script uses Playwright to launch a headless browser, navigate to a specified Notion page, and scrape its raw text content. It then cleans up the content by removing extraneous Notion UI elements and standardizing snippet separators. The cleaned content is saved to `notion.txt`.
2.  **Snippet Parsing & Selection (`send_email.py` - Integrated Logic):** A Python script reads `notion.txt`, identifies individual "snippets" based on a defined separator (`..`), and randomly selects a configurable number of them.
3.  **Multi-platform Notification (`send_email.py`):** The selected snippets are then formatted and sent as:
    * **Email:** Sent via SMTP using `smtplib`.
    * **Telegram Message:** Sent via the Telegram Bot API using the `requests` library.
4.  **Scheduled Automation (GitHub Actions):** A GitHub Actions workflow (`.github/workflows/scrape.yml`) orchestrates these steps, running daily at a specified time (e.g., 6 AM UTC) to ensure consistent delivery of new reminders.

---

## Getting Started: Replicate This Project

Want to set up your own daily reminders from a Notion page? Follow these steps!

### Prerequisites

Before you begin, ensure you have:

* A **GitHub account** to host your repository and run GitHub Actions.
* A **Notion page** with content you want to scrape. Ensure your content is structured with `..` on a new line to separate distinct snippets.
    * *Example Notion Structure:*
        ```
        Snippet 1 content here.
        This can be multiple lines.
        ..
        Snippet 2 content here.
        Could be a Hadith or a Dua.
        ..
        And so on.
        ```
* **Email Credentials:** An email account (e.g., Gmail) to send reminders from.
    * **For Gmail:** You may need to enable "Less secure app access" (older method) or, preferably, generate an [App Password](https://support.google.com/accounts/answer/185833) if you have 2-Factor Authentication enabled.
    * *If you're unsure how to get these, consider asking an AI assistant (like Gemini or ChatGPT): "How do I get an App Password for Gmail to send emails via SMTP?"*
* **Telegram Bot Token and Chat ID:** To send messages via Telegram.
    * You'll need to create a bot via Telegram's `@BotFather` and get its unique **Bot Token**.
    * You'll also need your personal (or a group's) **Chat ID**, which can be obtained using bots like `@RawDataBot` by interacting with it and checking its response, or by forwarding a message from the target chat to it.
    * *If you're unsure how to get these, consider asking an AI assistant (like Gemini or ChatGPT): "How do I create a Telegram bot and get my chat ID?"*

### Step 1: Create Your GitHub Repository and Add Files

1.  Create a new GitHub repository (or fork this one).
2.  Add the three core files to your repository in their respective paths:
    * `.github/workflows/scrape.yml`
    * `scrape_notion.js`
    * `send_email.py`

### Step 2: Add Repository Secrets

In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**. Click **"New repository secret"** and add the following secrets, using the exact names as shown in your screenshot:

* `EMAIL_PASS`
* `EMAIL_RECEIVER`
* `EMAIL_USER`
* `NOTION_PAGE_URL` (This is the URL of your Notion page)
* `TELEGRAM_BOT_TOKEN`
* `TELEGRAM_CHAT_ID`

### Step 3: Update Project Files

Navigate to each file in your repository and update its content as described below.

1.  **`.github/workflows/scrape.yml`:**
    * Ensure the `cron` schedule is set to your desired time (currently `0 6 * * *` for 6:00 AM UTC daily).
    * Verify that `NOTION_PAGE_URL` is passed as an environment variable to the `Scrape Notion page` step.
    * Confirm all email and Telegram secrets are passed to the `Send notification` step.
    * See the latest version of this file in your repository: [`./github/workflows/scrape.yml`](./.github/workflows/scrape.yml)

2.  **`scrape_notion.js`:**
    * Modify the `url` constant to read from the environment variable `NOTION_URL` (this variable is set in `.github/workflows/scrape.yml`).
    * Adjust the `filter` logic if your Notion page title or "Get Notion free" text varies from the defaults.
    * See the latest version of this file in your repository: [`./scrape_notion.js`](./scrape_notion.js)

3.  **`send_email.py`:**
    * Verify `NUM_SNIPPETS` is set to your desired number of snippets to include in the email and Telegram message.
    * Ensure the `telegram_message` variable is assigned `full_message_content` to send the complete parsed content to Telegram (not just a single snippet).
    * See the latest version of this file in your repository: [`./send_email.py`](./send_email.py)

### Step 4: Run and Verify

* Commit all your changes to your GitHub repository.
* Go to the "Actions" tab in your repository.
* Select the "Daily Notion Reminder" workflow.
* Click "Run workflow" (on the right side) to trigger a manual run and test your setup immediately.
* Check your email and Telegram for the reminders. Review the workflow logs for any errors.

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
