import smtplib, ssl, os, random, requests, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# --- Settings ---
# Constants for snippet history management
RECENCY_DAYS = 7
HISTORY_FILE = "sent_snippets.json"
# Adjustable: How many snippets you want in the email
NUM_SNIPPETS = 5  # Change this to 1, 2, 3...

# --- Load Credentials ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Snippet Parsing ---
# Read the entire content of notion.txt
with open("notion.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Normalize line endings
content = content.replace("\r\n", "\n").replace("\r", "\n")
lines = content.split("\n")
snippets = []
current = []

# Split by lines that equal ".."
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

# --- Load and Clean History (preserve last_sent_type separately)
try:
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    history = {}

last_sent_type = history.get("last_sent_type")

# Calculate cutoff datetime and keep only recent snippet entries
cutoff_dt = datetime.now() - timedelta(days=RECENCY_DAYS)
recent_history = {}
for key, val in history.items():
    if key == "last_sent_type":
        continue
    try:
        sent_dt = datetime.fromisoformat(val)
    except Exception:
        # skip entries with invalid timestamp
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

# Map to actual candidate lists
if target_category == "allah_says":
    primary_candidates = allah_says_snippets
    secondary_candidates = knowing_allah_snippets
else:
    primary_candidates = knowing_allah_snippets
    secondary_candidates = allah_says_snippets

# Filter primary candidates to exclude recent snippets
selection_pool = [s for s in primary_candidates if s not in recent_snippets]

# Fallback to other category if not enough
if len(selection_pool) < NUM_SNIPPETS:
    print(f"⚠️ Warning: Not enough fresh snippets in target category '{target_category}'. Trying fallback category.")
    selection_pool = [s for s in secondary_candidates if s not in recent_snippets]

# If still not enough, fall back to any non-recent snippet from all snippets
if len(selection_pool) < NUM_SNIPPETS:
    print("⚠️ Warning: Both categories exhausted of fresh snippets. Falling back to any non-recent snippets.")
    selection_pool = [s for s in snippets if s not in recent_snippets]

# Final fallback: allow repeats from full pool to guarantee NUM_SNIPPETS
if len(selection_pool) < NUM_SNIPPETS:
    print("⚠️ Warning: Not enough non-recent snippets available. Allowing repeats from full pool.")
    selection_pool = snippets

if not selection_pool:
    raise Exception("❌ No snippets available for selection!")

# Choose random N snippets
selected_snippets = random.sample(selection_pool, min(NUM_SNIPPETS, len(selection_pool)))

# Mark repeated snippets for display (if they were sent within cutoff window)
display_snippets = []
for s in selected_snippets:
    if s in recent_snippets:
        display_snippets.append("Repeated this week: " + s)
    else:
        display_snippets.append(s)

# Join them for the email body AND Telegram message
full_message_content = "\n\n---\nIn other news...\n\n".join(display_snippets)

# --- Update history: record selected snippets and last_sent_type
current_time = datetime.now().isoformat()
# start with recent_history (pruned) and add/update entries
new_history = dict(recent_history)
for snippet in selected_snippets:
    new_history[snippet] = current_time
# set today's category
new_history["last_sent_type"] = target_category

# Write updated history back to file so the workflow can commit it
with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    json.dump(new_history, f, indent=2)
print("✅ Updated snippet history.")

# --- Send Email ---
if EMAIL_USER and EMAIL_PASS and EMAIL_RECEIVER:
    print("\n📬 Preparing to send email...")
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "🌙 Your Daily Islamic Reminder"
    msg.attach(MIMEText(full_message_content, "plain")) # <--- Used new variable here

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_RECEIVER, msg.as_string())
        print("✅ Email sent successfully.")
        print("📤 Sent content:\n")
        print(full_message_content) # <--- Used new variable here

        # (history already updated earlier)
            
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
else:
    print("⚠️ Email credentials not found. Skipping email.")

# --- Send Telegram Message ---
if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    print("\n✈️ Preparing to send Telegram message...")
    # Now using the same full content for Telegram
    telegram_message = full_message_content # <--- THIS IS THE KEY CHANGE

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": telegram_message,
        "parse_mode": "Markdown"  # Or "HTML" if you prefer
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("✅ Telegram message sent successfully.")
            print("📤 Sent content:\n")
            print(telegram_message)
        else:
            print(f"❌ Failed to send Telegram message. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
else:
    print("⚠️ Telegram credentials not found. Skipping Telegram message.")
