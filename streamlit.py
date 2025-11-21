import streamlit as st
import pandas as pd

# Import dataframe
sbusports = pd.read_csv('raw/sixmetricsclass.csv')

# Ensure timestamp column is datetime
sbusports['timestamp'] = pd.to_datetime(sbusports['timestamp'])

# Sidebar selection for groupteam (restricted options)
group_options = ["All"] + sbusports['groupteam'].unique().tolist()
group_choice = st.sidebar.selectbox("Select a Group Team", group_options, index=0)

# Filter dataframe based on groupteam
if group_choice == "All":
    team_df = sbusports.copy()
else:
    team_df = sbusports[sbusports['groupteam'] == group_choice]

# Sidebar selection for playername (default "All")
player_options = ["All"] + team_df['playername'].unique().tolist()
player_choice = st.sidebar.selectbox("Select a Player", player_options, index=0)

# Filter dataframe based on playername
if player_choice == "All":
    filtered_df = team_df.copy()
else:
    filtered_df = team_df[team_df['playername'] == player_choice]

# Sidebar date range filter
min_date = sbusports['timestamp'].min().date()
max_date = sbusports['timestamp'].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply date filter
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['timestamp'].dt.date >= start_date) &
        (filtered_df['timestamp'].dt.date <= end_date)
    ]

st.subheader(f"Metrics for {group_choice} - {player_choice} ({start_date} to {end_date})")

# Define the six metrics you want to plot
metrics_to_plot = [
    "Speed_Max",
    "Jump Height(M)",
    "Mrsi",
    "Peak Velocity(M/S)",
    "Peak Propulsive Power(W)",
    "Distance_Total"
]

# Loop through each metric and create a line chart
for metric in metrics_to_plot:
    metric_df = filtered_df[filtered_df['metric'] == metric]
    if not metric_df.empty:
        st.write(f"### {metric}")
        st.line_chart(metric_df, x='timestamp', y='value')
    else:
        st.write(f"### {metric} (no data available)")