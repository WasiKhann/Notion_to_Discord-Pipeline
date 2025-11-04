# Notion-to-Discord Pipeline

<p align="center">
  <img src="./assets/icon.png" alt="Project Icon" width="300">
</p>

<p align="center">
  <strong>An automated, dual-stream content pipeline that scrapes curated snippets from Notion and delivers them to designated Discord channels.</strong>
  <br>
  <!-- Corrected URLs with hyphens instead of spaces -->
  <a href="https://github.com/WasiKhann/Notion_to_Discord-Pipeline/actions/workflows/scrape.yml">
    <img src="https://github.com/WasiKhann/Notion_to_Discord-Pipeline/actions/workflows/scrape.yml/badge.svg" alt="Build Status">
  </a>
</p>

---

## 🌟 Project Overview

**Notion-to-Discord Pipeline** is a robust automation system designed to bridge the gap between your personal knowledge base in Notion and your community on Discord. It runs a daily GitHub Actions workflow that processes two independent content streams ("Deen" for spiritual content and "Dunya" for general content), ensuring that fresh, curated insights are delivered automatically without manual intervention.

This project demonstrates a full CI/CD pipeline, from headless browser scraping and data processing to state management and secure credential handling.

## ✨ Key Features

- **Dual-Stream Processing**: Runs two independent jobs sequentially (`Deen` → `Dunya`) to scrape, process, and deliver content from separate Notion pages to separate Discord channels.
- **Smart Snippet Selection**:
    - **Guaranteed Count**: Delivers exactly 10 snippets per day, per stream.
    - **Intelligent Deduplication**: Avoids sending variations of the same core message by grouping snippets that start with the same line.
    - **Content-Aware Alternation**: Alternates between predefined content categories to ensure variety.
    - **7-Day Memory**: Tracks sent snippets in a JSON history file to prevent repeats within a week.
- **Robust Message Handling**: Automatically splits content into multiple messages to respect Discord's 2000-character limit, ensuring all 10 snippets are delivered.
- **Fully Automated**: Uses a `cron`-scheduled GitHub Actions workflow for a "set it and forget it" daily execution.
- **Secure Configuration**: Manages all sensitive URLs and tokens using encrypted GitHub Secrets.

## 🛠️ Tech Stack

- **Automation & CI/CD**: GitHub Actions
- **Web Scraping**: Node.js with **Playwright** (for robust, headless browser automation)
- **Data Processing & Logic**: Python
- **Notifications**: Discord Webhooks
- **State Management**: Git & JSON

## 🚀 Getting Started

You can easily fork this repository and set up your own automated Notion-to-Discord pipeline.

### Prerequisites

- A GitHub account
- One or two Notion pages (publicly shared to the web - not indexed for search engine adds "privacy")
- One or two Discord channels with webhook URLs

### Setup Guide

1.  **Fork the Repository**:
    Click the "Fork" button at the top-right of this page to create your own copy.

2.  **Prepare Your Notion Content**:
    On your Notion page(s), separate individual snippets by placing `..` on a new line.

    ```
    This is the first snippet.
    It can have multiple lines.
    ..
    This is the second snippet.
    ```

3.  **Create Discord Webhooks**:
    In your Discord channel settings, go to `Integrations` > `Webhooks` > `New Webhook`, and copy the Webhook URL.

4.  **Configure GitHub Secrets**:
    In your forked repository, go to `Settings` > `Secrets and variables` > `Actions` and add the following four secrets:

    - `NOTION_PAGE_URL_DEEN`: URL for your first Notion page.
    - `DISCORD_WEBHOOK_URL_DEEN`: Discord webhook for your first channel.
    - `NOTION_PAGE_URL_DUNYA`: URL for your second Notion page.
    - `DISCORD_WEBHOOK_URL_DUNYA`: Discord webhook for your second channel.

    *Note: If you only want one stream, you can use the same URLs for both `_DEEN` and `_DUNYA` secrets.*

5.  **Activate the Workflow**:
    Go to the **Actions** tab of your repository. If prompted, enable workflows. The `Daily Notion Reminder` workflow is now ready. It will run automatically every day at midnight UTC, or you can trigger it manually by clicking "Run workflow".

## 📫 Contact

Wasi Khan

- **GitHub**: [@WasiKhann](https://github.com/WasiKhann)
- **LinkedIn**: [wasi-khann](https://www.linkedin.com/in/wasi-khann/)

---