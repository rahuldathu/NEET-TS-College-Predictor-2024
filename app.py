import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ------------------ Google Sheets Logging Setup ------------------

def init_gsheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    json_creds = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(json_creds, scopes=scope)
    client = gspread.authorize(creds)
    return client

def get_or_create_worksheet(spreadsheet, title, rows=100, cols=10):
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)

def log_to_gsheet(rank, category, gender, entry_channel):
    client = init_gsheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        spreadsheet = client.open("Neet_Predictor_log_Streamlit")
        worksheet = get_or_create_worksheet(spreadsheet, "Sheet2")
        worksheet = spreadsheet.worksheet("Sheet2")  # Refer to Sheet2 by name
        worksheet.append_row([timestamp, rank, category, gender, entry_channel])
    except Exception as e:
        st.error(f"❌ Failed to log to Sheet2: {e}")

# ------------------ Streamlit App ------------------

# Load inference table
df = pd.read_csv("inference_aggregated.csv")

# Streamlit page config
st.set_page_config(page_title="NEET College Predictor", layout="centered")

# Page title centered
st.markdown(
    """
    <div style='text-align:center; font-weight:bold; font-size:3em; line-height:1.2;'>
        🎓 NEET College Predictor<br>(Telangana)
    </div>
    """,
    unsafe_allow_html=True
)

# Centered subheading
st.markdown("<h4 style='text-align:center;'>Enter Your Details</h4>", unsafe_allow_html=True)

# Create 3 columns for centering form fields
left, center, right = st.columns([1, 2, 1])

with center:
    category_options = sorted(df["Candidate Category"].dropna().unique())
    gender_options = sorted(df["Gender"].dropna().unique())
    entry_options = sorted(df["Entry Channel"].dropna().unique())

    default_category = "OPEN" if "OPEN" in category_options else category_options[0]
    default_gender = "GEN" if "GEN" in gender_options else gender_options[0]
    default_entry = "GEN" if "GEN" in entry_options else entry_options[0]

    candidate_category = st.selectbox("Candidate Category", category_options, index=category_options.index(default_category), key="cat")
    gender = st.selectbox("Gender", gender_options, index=gender_options.index(default_gender), key="gen")
    entry_channel = st.selectbox("Entry Channel", entry_options, index=entry_options.index(default_entry), key="ent")
    rank = st.number_input("Your NEET Rank", min_value=1, step=1, key="rank_input")

    # ✅ The one and only working, aligned button
    predict = st.button("🔍 Predict Possible Colleges")

# Trigger prediction logic only when the button is pressed
if predict:
    # Filter dataset based on inputs
    filtered_df = df[
        (df["Candidate Category"] == candidate_category) &
        (df["Gender"] == gender) &
        (df["Entry Channel"] == entry_channel) &
        (df["Max_Rank"] >= rank)
    ]

    filtered_df = filtered_df.sort_values("Percentile_40th", ascending=True)
    filtered_df["College"] = filtered_df["College"].str.replace(r"^\d+\.\s*", "", regex=True)

    st.markdown(f"### 🎯 Matching Colleges for Rank **{rank}**")

    if filtered_df.empty:
        st.warning("No matching colleges found for the selected criteria.")
    else:
        display_df = filtered_df[[
            "College", "Candidate Category", "Min_Rank", "Max_Rank", "Count", "Percentile_40th", "Probable_Round"
        ]].rename(columns={
            "Min_Rank": "Min_Rank",
            "Max_Rank": "Max_Rank",
            "Count": "no of Students allotted",
            "Percentile_40th": "40th Percentile Rank",
            "Probable_Round": "Round"
        })

        st.dataframe(display_df.iloc[:, :].reset_index(drop=True), use_container_width=True)

    # Log to Google Sheets
    try:
        log_to_gsheet(rank, candidate_category, gender, entry_channel)
        st.success("✅ Your query was logged successfully.")
    except Exception as e:
        st.error(f"❌ Failed to log query: {e}")
