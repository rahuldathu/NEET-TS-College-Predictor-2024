import pandas as pd
import numpy as np

# Load the raw CSV data
input_file = "cleaned_data.csv"  # Replace with your actual filename
df = pd.read_csv(input_file)

# Rename columns for consistency
df = df.rename(columns={
    "Allotted Category": "Candidate Category",
    "Gender Reservation": "Gender",
    "Entry Channel": "Entry Channel",
    "Rank": "Rank",
    "College": "College",
    "Allocation Round": "Allocation Round"
})

# Treat null Entry Channel as 'GEN'
df["Entry Channel"] = df["Entry Channel"].fillna("GEN")

# Group by relevant columns and compute metrics
grouped = df.groupby(["College", "Candidate Category", "Gender", "Entry Channel"])

aggregated = grouped.agg(
    Count=("Rank", "size"),  # Number of students securing a seat in that set
    Min_Rank=("Rank", "min"),
    Max_Rank=("Rank", "max"),
    Percentile_40th=("Rank", lambda x: np.percentile(x, 40)),
    Probable_Round=("Allocation Round", lambda x: x.mode().iat[0] if not x.mode().empty else "Unknown")
).reset_index()

# Save aggregated results
aggregated.to_csv("inference_aggregated.csv", index=False)
print("✅ inference_aggregated.csv generated with accurate student count per college/category/gender/entry set.")
