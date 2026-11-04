
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client

st.title("Kochi Air Quality Dashboard")

# Supabase connection
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_PUBLISHABLE_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Open-Meteo API
url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=9.93&longitude=76.27&hourly=pm10,pm2_5,us_aqi&timezone=Asia%2FKolkata&past_days=7"

# Fetch and insert data
if st.button("Fetch and Save Data"):

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data["hourly"])

    df["time"] = pd.to_datetime(df["time"])

    # Convert time to UTC for Supabase
    df["time"] = (
        df["time"]
        .dt.tz_localize("Asia/Kolkata")
        .dt.tz_convert("UTC")
        .dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    # Handle missing values
    df = df.astype(object).where(pd.notna(df), None)

    # Insert or update records
    records = df.to_dict(orient="records")

    supabase.table("kochi_air_quality").upsert(
        records,
        on_conflict="time"
    ).execute()

    st.success("Data inserted into Supabase successfully!")

# Retrieve data from Supabase
st.header("Air Quality Data from Supabase")

result = (
    supabase.table("kochi_air_quality")
    .select("*")
    .order("time")
    .limit(1000)
    .execute()
)

df = pd.DataFrame(result.data)

if not df.empty:

    df["time"] = pd.to_datetime(df["time"], utc=True)
    df["time"] = df["time"].dt.tz_convert("Asia/Kolkata")

    st.dataframe(df)

    # Statistical analysis
    st.header("Statistical Analysis")

    st.write(
        df[["us_aqi", "pm2_5", "pm10"]].describe()
    )

    # Average values
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average AQI",
        round(df["us_aqi"].mean(), 2)
    )

    col2.metric(
        "Average PM2.5",
        round(df["pm2_5"].mean(), 2)
    )

    col3.metric(
        "Average PM10",
        round(df["pm10"].mean(), 2)
    )

    # AQI chart
    st.header("AQI Time Series")

    fig, ax = plt.subplots()

    ax.plot(df["time"], df["us_aqi"])

    ax.set_xlabel("Time")
    ax.set_ylabel("AQI")
    ax.set_title("AQI Changes Over Time")

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    # PM2.5 and PM10 chart
    st.header("PM2.5 and PM10")

    fig, ax = plt.subplots()

    ax.plot(df["time"], df["pm2_5"], label="PM2.5")
    ax.plot(df["time"], df["pm10"], label="PM10")

    ax.set_xlabel("Time")
    ax.set_ylabel("Pollution Level")
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.success("Air Quality Dashboard Completed")

else:
    st.info("Click Fetch and Save Data to retrieve records.")
