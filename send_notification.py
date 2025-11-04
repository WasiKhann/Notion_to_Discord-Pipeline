import os
import random
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict
from itertools import groupby

# --- Settings ---
RECENCY_DAYS = 7
NUM_SNIPPETS = 10  # Required number of snippets per day
DISCORD_CHAR_LIMIT = 1900  # Safe buffer below Discord's 2000 char limit
SNIPPET_SEPARATOR = "\n---\n"  # Clean separator between snippets
MESSAGE_DELAY = 1  # Seconds to wait between sending multiple messages

# --- Stream Configuration ---
STREAM_PREFIX = os.getenv("STREAM_PREFIX")
if not STREAM_PREFIX:
    raise Exception("❌ ERROR: STREAM_PREFIX environment variable is not set! Must be 'DEEN' or 'DUNYA'")

# Dynamic file paths based on stream
NOTION_FILE = f"notion_{STREAM_PREFIX}.txt"
HISTORY_FILE = f"sent_snippets_{STREAM_PREFIX}.json"

print(f"\n🌊 Processing {STREAM_PREFIX} stream")
print(f"  - Reading from: {NOTION_FILE}")
print(f"  - History file: {HISTORY_FILE}")

# --- Helper Functions ---
def get_first_line(snippet: str) -> str:
    """Extract the first line of a snippet for grouping."""
    return snippet.strip().split('\n')[0]

def deduplicate_by_first_line(snippets: List[str]) -> List[str]:
    """Group snippets by first line and randomly select one from each group."""
    # Sort snippets by their first line to use groupby
    sorted_snippets = sorted(snippets, key=get_first_line)
    # Group by first line and randomly select one from each group
    deduplicated = []
    for _, group in groupby(sorted_snippets, key=get_first_line):
        deduplicated.append(random.choice(list(group)))
    return deduplicated

def chunk_messages(snippets: List[str], char_limit: int) -> List[str]:
    """Split snippets into multiple messages respecting the character limit."""
    messages = []
    current_message = []
    current_length = 0
    
    for snippet in snippets:
        # Calculate length with separator if not first snippet in message
        new_length = (current_length + len(snippet) + 
                     (len(SNIPPET_SEPARATOR) if current_message else 0))
        
        if new_length <= char_limit:
            current_message.append(snippet)
            current_length = new_length
        else:
            # Finalize current message and start new one
            if current_message:
                messages.append(SNIPPET_SEPARATOR.join(current_message))
            current_message = [snippet]
            current_length = len(snippet)
    
    # Add final message if there are remaining snippets
    if current_message:
        messages.append(SNIPPET_SEPARATOR.join(current_message))
    
    return messages

# --- Load Credentials ---
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
if not DISCORD_WEBHOOK_URL:
    raise Exception(f"❌ ERROR: DISCORD_WEBHOOK_URL environment variable is not set for {STREAM_PREFIX} stream!")

# --- Snippet Parsing ---
try:
    with open(NOTION_FILE, "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    raise Exception(f"❌ ERROR: Could not find {NOTION_FILE}. Make sure the scraping step completed successfully.")
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
snippets = [s for s in snippets if "Add new pt" not in s]

if not snippets:
    raise Exception("❌ No snippets found. Check that your notion page(s) contains separator lines with '..'.")

print(f"🧪 Found {len(snippets)} valid snippet(s) after filtering unwanted entries.")

# --- Categorize snippets
# --- Categorize and deduplicate snippets
print("\n🔍 Categorizing and deduplicating snippets...")

# Initial categorization
allah_says_snippets = [s for s in snippets if s.strip().startswith("Allah says\n")]
knowing_allah_snippets = [s for s in snippets if s.strip().startswith("Knowing Allah, your Rab is the key")]
other_snippets = [s for s in snippets if s not in allah_says_snippets and s not in knowing_allah_snippets]

# Apply targeted deduplication for specific categories
filtered_allah_says = deduplicate_by_first_line(allah_says_snippets)
filtered_knowing_allah = deduplicate_by_first_line(knowing_allah_snippets)

print(f"📊 Initial counts:")
print(f"  - Allah says snippets: {len(allah_says_snippets)} → {len(filtered_allah_says)} after deduplication")
print(f"  - Knowing Allah snippets: {len(knowing_allah_snippets)} → {len(filtered_knowing_allah)} after deduplication")
print(f"  - Other snippets: {len(other_snippets)}")

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

print(f"\n📅 Recent history:")
print(f"  - {len(recent_history)} snippets sent in the last {RECENCY_DAYS} days")
print(f"  - Last category sent: {last_sent_type or 'None (first run)'}")

# --- Build selection pool with strict priority order
print("\n🎯 Building selection pool...")

# Determine today's target category
if last_sent_type == "knowing_allah":
    target_category = "allah_says"
    primary_pool = filtered_allah_says
    secondary_pool = filtered_knowing_allah
elif last_sent_type == "allah_says":
    target_category = "knowing_allah"
    primary_pool = filtered_knowing_allah
    secondary_pool = filtered_allah_says
else:
    target_category = "allah_says"
    primary_pool = filtered_allah_says
    secondary_pool = filtered_knowing_allah

print(f"  Target category: {target_category}")

# Initialize final selection list
snippets_to_send = []

# Step 1: Add from primary category (non-recent)
primary_available = [s for s in primary_pool if s not in recent_snippets]
snippets_to_send.extend(primary_available)
print(f"  - Added {len(primary_available)} from primary category")

# Step 2: Add from secondary category (non-recent)
if len(snippets_to_send) < NUM_SNIPPETS:
    slots_remaining = NUM_SNIPPETS - len(snippets_to_send)
    secondary_available = [s for s in secondary_pool if s not in recent_snippets]
    snippets_to_send.extend(secondary_available[:slots_remaining])
    print(f"  - Added {min(len(secondary_available), slots_remaining)} from secondary category")

# Step 3: Add from other snippets (non-recent)
if len(snippets_to_send) < NUM_SNIPPETS:
    slots_remaining = NUM_SNIPPETS - len(snippets_to_send)
    other_available = [s for s in other_snippets if s not in recent_snippets]
    snippets_to_send.extend(other_available[:slots_remaining])
    print(f"  - Added {min(len(other_available), slots_remaining)} from other snippets")

# Step 4: Final fallback - add recent snippets if necessary
if len(snippets_to_send) < NUM_SNIPPETS:
    print("\n⚠️ Not enough non-recent snippets. Adding recent snippets to reach target count...")
    
    slots_remaining = NUM_SNIPPETS - len(snippets_to_send)
    
    # Try primary category first
    remaining_primary = [s for s in primary_pool if s not in snippets_to_send]
    snippets_to_send.extend(remaining_primary[:slots_remaining])
    
    # Then secondary
    if len(snippets_to_send) < NUM_SNIPPETS:
        slots_remaining = NUM_SNIPPETS - len(snippets_to_send)
        remaining_secondary = [s for s in secondary_pool if s not in snippets_to_send]
        snippets_to_send.extend(remaining_secondary[:slots_remaining])
    
    # Finally other snippets
    if len(snippets_to_send) < NUM_SNIPPETS:
        slots_remaining = NUM_SNIPPETS - len(snippets_to_send)
        remaining_other = [s for s in other_snippets if s not in snippets_to_send]
        snippets_to_send.extend(remaining_other[:slots_remaining])

# Shuffle final selection
random.shuffle(snippets_to_send)
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

# Shuffle the selection pool for randomization
random.shuffle(selection_pool)

# Initialize variables for iterative message building
final_snippets_to_send = []
current_length = 0

# Process each snippet, respecting character limits
for snippet in selection_pool:
    # Prepare the snippet (mark if repeated)
    display_snippet = "Repeated this week: " + snippet if snippet in recent_snippets else snippet
    
    # Calculate new length including separator if not the first snippet
    new_content_length = (
        current_length + 
        len(display_snippet) + 
        (len(SNIPPET_SEPARATOR) if final_snippets_to_send else 0)
    )
    
    # Check if adding this snippet would exceed the limit
    if new_content_length <= DISCORD_CHAR_LIMIT:
        final_snippets_to_send.append(display_snippet)
        current_length = new_content_length
        
        # Stop if we've reached the desired number of snippets
        if len(final_snippets_to_send) >= NUM_SNIPPETS:
            break
    else:
        # Stop if adding this snippet would exceed the limit
        break

# Check if we have enough snippets
if not snippets_to_send:
    raise Exception("❌ Critical: No snippets available for selection!")

if len(snippets_to_send) < NUM_SNIPPETS:
    print(f"\n⚠️ Warning: Could only find {len(snippets_to_send)} snippets (target: {NUM_SNIPPETS})")

# Split content into message chunks
print("\n📝 Preparing messages...")
message_chunks = chunk_messages(snippets_to_send, DISCORD_CHAR_LIMIT)
print(f"  - Content will be split into {len(message_chunks)} message(s)")

# --- Update history: record selected snippets and last_sent_type
current_time = datetime.now().isoformat()
new_history = dict(recent_history)
for snippet in snippets_to_send:
    new_history[snippet] = current_time
new_history["last_sent_type"] = target_category

with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    json.dump(new_history, f, indent=2)
print("✅ Updated snippet history")

# --- Send messages to Discord webhook ---
if DISCORD_WEBHOOK_URL:
    print(f"\n🚀 Sending {len(message_chunks)} message(s) to Discord webhook...")
    
    for i, message_content in enumerate(message_chunks, 1):
        try:
            print(f"  - Sending message {i}/{len(message_chunks)} "
                  f"({len(message_content)}/{DISCORD_CHAR_LIMIT} chars)...")
            
            resp = requests.post(DISCORD_WEBHOOK_URL, 
                               json={"content": message_content})
            
            if 200 <= resp.status_code < 300:
                print(f"    ✅ Message {i} sent successfully")
            else:
                print(f"    ❌ Failed to send message {i}. "
                      f"Status: {resp.status_code}, Response: {resp.text}")
                break  # Stop sending if we encounter an error
                
            # Add delay between messages (except after the last one)
            if i < len(message_chunks):
                time.sleep(MESSAGE_DELAY)
                
        except Exception as e:
            print(f"    ❌ Exception while sending message {i}: {e}")
            break  # Stop sending if we encounter an error
            
    print(f"\n📊 Summary:")
    print(f"  - Selected {len(snippets_to_send)} snippets")
    print(f"  - Split into {len(message_chunks)} message(s)")
    print(f"  - Used separator: '{SNIPPET_SEPARATOR}'")
else:
    print("⚠️ DISCORD_WEBHOOK_URL not set. Skipping Discord notification.")
