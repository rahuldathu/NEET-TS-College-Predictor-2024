import re
import pandas as pd
from pdfminer.high_level import extract_text

# === Step 1: Extract text ===
pdf_path = "data.pdf"
text = extract_text(pdf_path)

# === Step 2: Split by college ===
college_blocks = re.split(r'\nCOLL\s+::\s+', text)[1:]

parsed_data = []

for block in college_blocks:
    lines = block.strip().splitlines()
    college_name = lines[0].strip()
    for line in lines:
        if re.match(r'^\d{3,6}\s+\d{10}', line):
            parsed_data.append((college_name, line.strip()))

# === Step 3: Parse with regex ===
columns = [
    "College", "Rank", "Roll No", "Student Name", "Category", "Sex",
    "Minority", "PH", "NCC", "CAP", "PMC", "ANG", "SCL", "EWS", "Admission Details"
]

structured_rows = []
skipped_lines = []

pattern = re.compile(
    r"^(?P<rank>\d{3,6})\s+"
    r"(?P<roll>\d{10})\s+"
    r"(?P<name>.+?)\s{2,}"
    r"(?P<rest>.+)$"
)

for college, row in parsed_data:
    match = pattern.match(row)
    if not match:
        skipped_lines.append(f"[{college}] -> {row}")
        continue

    rank = match.group("rank")
    roll = match.group("roll")
    name = match.group("name").strip()
    rest = match.group("rest").strip().split()

    rest += [pd.NA] * (len(columns) - 4 - len(rest))  # pad
    fields = [college, rank, roll, name] + rest[:len(columns) - 4]
    structured_rows.append(fields)

# === Step 4: Save output ===
df = pd.DataFrame(structured_rows, columns=columns)
df.to_csv("telangana_mopup_allocations.csv", index=False)

with open("skipped_rows.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(skipped_lines))

print(f"✅ Done. Saved {len(df)} rows to CSV.")
print(f"⚠️  Skipped {len(skipped_lines)} rows to skipped_rows.txt")
