import streamlit as st
import pandas as pd
import altair as alt

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

# Sidebar selection for playername (multi-select with "All")
player_options = ["All"] + team_df['playername'].unique().tolist()
player_choice = st.sidebar.multiselect("Select Player(s)", player_options, default=["All"])

# Filter dataframe based on player selection
if "All" in player_choice:
    filtered_df = team_df.copy()
else:
    filtered_df = team_df[team_df['playername'].isin(player_choice)]

# Sidebar year filter (buttons)
years = sorted(sbusports['timestamp'].dt.year.unique())
year_choice = st.sidebar.radio("Select Year", ["All"] + years, index=0)

# Apply year filter
if year_choice != "All":
    filtered_df = filtered_df[filtered_df['timestamp'].dt.year == year_choice]

st.subheader(f"Metrics for {group_choice} - {', '.join(player_choice)}")

# Define the six metrics you want to plot
metrics_to_plot = [
    "Speed_Max",
    "Jump Height(M)",
    "Mrsi",
    "Peak Velocity(M/S)",
    "Peak Propulsive Power(W)",
    "Distance_Total"
]

# Loop through each metric and create a line chart with trend line
for metric in metrics_to_plot:
    metric_df = filtered_df[filtered_df['metric'] == metric]
    if not metric_df.empty:
        st.write(f"### {metric}")
        
        # Base line chart
        line = alt.Chart(metric_df).mark_line(point=True).encode(
            x='timestamp:T',
            y='value:Q',
            color='playername:N'
        )
        
        # Trend line (linear regression)
        trend = line.transform_regression('timestamp', 'value').mark_line(color='red')
        
        chart = line + trend
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write(f"### {metric} (no data available)")