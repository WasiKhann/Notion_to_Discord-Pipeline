import os
import random
import requests
import json
from datetime import datetime, timedelta

# --- Settings ---
RECENCY_DAYS = 7
HISTORY_FILE = "sent_snippets.json"
NUM_SNIPPETS = 5

# --- Load Credentials ---
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# --- Snippet Parsing ---
with open("notion.txt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("\r\n", "\n").replace("\r", "\n")
lines = content.split("\n")
snippets = []
current = []

for line in lines:
    if line.strip() == "..":
        if current:
            snippet = "\n".join(current).strip()
            if snippet:
                snippets.append(snippet)
            current = []
    else:
        current.append(line)
if current:
    snippet = "\n".join(current).strip()
    if snippet:
        snippets.append(snippet)

# --- Filter out permanently excluded snippets
snippets = [s for s in snippets if "Add new point" not in s]

if not snippets:
    raise Exception("❌ No snippets found. Check that notion.txt contains separator lines with '..'.")

print(f"🧪 Found {len(snippets)} valid snippet(s) after filtering unwanted entries.")

# --- Categorize snippets
allah_says_snippets = [s for s in snippets if s.strip().startswith("Allah says\n“If you avoid the major sins which you are forbidden.")]
knowing_allah_snippets = [s for s in snippets if s.strip().startswith("Knowing Allah, your Rab is the key")]

# --- Load and Clean History
try:
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    history = {}

last_sent_type = history.get("last_sent_type")

cutoff_dt = datetime.now() - timedelta(days=RECENCY_DAYS)
recent_history = {}
for key, val in history.items():
    if key == "last_sent_type":
        continue
    try:
        sent_dt = datetime.fromisoformat(val)
    except Exception:
        continue
    if sent_dt >= cutoff_dt:
        recent_history[key] = val

recent_snippets = set(recent_history.keys())

print(f"📊 Status: {len(snippets)} total snippets")
print(f"🔒 {len(recent_history)} recent snippets excluded")
print(f"✨ {len(snippets) - len(recent_history)} snippets available (category filtering applied below)")

# --- Determine today's target category (alternate)
if last_sent_type == "knowing_allah":
    target_category = "allah_says"
elif last_sent_type == "allah_says":
    target_category = "knowing_allah"
else:
    target_category = "allah_says"

if target_category == "allah_says":
    primary_candidates = allah_says_snippets
    secondary_candidates = knowing_allah_snippets
else:
    primary_candidates = knowing_allah_snippets
    secondary_candidates = allah_says_snippets

selection_pool = [s for s in primary_candidates if s not in recent_snippets]

if len(selection_pool) < NUM_SNIPPETS:
    print(f"⚠️ Warning: Not enough fresh snippets in target category '{target_category}'. Trying fallback category.")
    selection_pool = [s for s in secondary_candidates if s not in recent_snippets]

if len(selection_pool) < NUM_SNIPPETS:
    print("⚠️ Warning: Both categories exhausted of fresh snippets. Falling back to any non-recent snippets.")
    selection_pool = [s for s in snippets if s not in recent_snippets]

if len(selection_pool) < NUM_SNIPPETS:
    print("⚠️ Warning: Not enough non-recent snippets available. Allowing repeats from full pool.")
    selection_pool = snippets

if not selection_pool:
    raise Exception("❌ No snippets available for selection!")

selected_snippets = random.sample(selection_pool, min(NUM_SNIPPETS, len(selection_pool)))

display_snippets = []
for s in selected_snippets:
    if s in recent_snippets:
        display_snippets.append("Repeated this week: " + s)
    else:
        display_snippets.append(s)

full_message_content = "\n\n---\nIn other news...\n\n".join(display_snippets)

# --- Update history: record selected snippets and last_sent_type
current_time = datetime.now().isoformat()
new_history = dict(recent_history)
for snippet in selected_snippets:
    new_history[snippet] = current_time
new_history["last_sent_type"] = target_category

with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    json.dump(new_history, f, indent=2)
print("✅ Updated snippet history.")

# --- Send to Discord webhook ---
if DISCORD_WEBHOOK_URL:
    print("\n🚀 Sending notification to Discord webhook...")
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json={"content": full_message_content})
        if 200 <= resp.status_code < 300:
            print("✅ Discord notification sent successfully.")
        else:
            print(f"❌ Failed to send Discord notification. Status: {resp.status_code}, Response: {resp.text}")
    except Exception as e:
        print(f"❌ Exception while sending Discord notification: {e}")
else:
    print("⚠️ DISCORD_WEBHOOK_URL not set. Skipping Discord notification.")
