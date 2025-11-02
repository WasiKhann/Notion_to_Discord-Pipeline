import random

# Step 1: Read lines
with open("notion.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Step 2: Group snippets manually
snippets = []
current_snippet = []

for line in lines:
    if line.rstrip("\n") in ("..", ".. "):  # exact match, preserving space
        if current_snippet:
            snippet = "".join(current_snippet).strip()
            if snippet:
                snippets.append(snippet)
            current_snippet = []
    else:
        current_snippet.append(line)

# Step 3: Catch the last block if needed
if current_snippet:
    snippet = "".join(current_snippet).strip()
    if snippet:
        snippets.append(snippet)

# Step 4: Confirm and pick one
if not snippets:
    raise Exception("❌ No snippets found. Check your separator format.")

print(f"🧪 Found {len(snippets)} valid snippets.\n")
chosen = random.choice(snippets)
print("🎯 Selected snippet:\n")
print(chosen)

# Step 5: Save chosen snippet to file
with open("picked_snippet.txt", "w", encoding="utf-8") as f:
    f.write(chosen)
