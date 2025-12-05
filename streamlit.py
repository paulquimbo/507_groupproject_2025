import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta

# Cache data loading for performance
@st.cache_data
def load_data():
    df = pd.read_csv('raw/fivemetrics_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by="playername")
    return df

# Import dataframe
sbusports = load_data()
sbusports['timestamp'] = pd.to_datetime(sbusports['timestamp'])
sbusports = sbusports.sort_values(by="playername")

# Add combined label column for display
sbusports['player_label'] = sbusports['playername'] + " (" + sbusports['groupteam'] + ")"

# Sidebar selection for groupteam
group_options = ["All"] + sorted(sbusports['groupteam'].unique().tolist())
group_choice = st.sidebar.selectbox("Select a Group Team", group_options, index=0)

team_df = sbusports if group_choice == "All" else sbusports[sbusports['groupteam'] == group_choice]

# Checkbox to toggle restricted player list
restrict_players = st.sidebar.checkbox("Check Box for Selected Players", value=False)

# Define your 4 selected players
selected_players = ['PLAYER_741', 'PLAYER_555', 'PLAYER_755', 'PLAYER_995']

# Build player options
if restrict_players:
    player_options = ["All"] + sorted(selected_players)
else:
    player_options = ["All"] + sorted(team_df['playername'].unique().tolist())

# Sidebar selection for playername (multi-select)
player_choice = st.sidebar.multiselect("Select Player(s)", player_options, default=["All"])

# Filter logic
if "All" in player_choice:
    if restrict_players:
        filtered_df = team_df[team_df['playername'].isin(selected_players)]
    else:
        filtered_df = team_df
else:
    filtered_df = team_df[team_df['playername'].isin(player_choice)]

# Sidebar year filter (radio buttons)
years = sorted(sbusports['timestamp'].dt.year.unique())
year_choice = st.sidebar.radio("Select Year", ["All"] + years, index=0)

if year_choice != "All":
    filtered_df = filtered_df[filtered_df['timestamp'].dt.year == year_choice]

# --- NEW: Predefined date range choices ---
range_options = {
    "Past Month": timedelta(days=30),
    "Past 3 Months": timedelta(days=90),
    "Past 6 Months": timedelta(days=180),
    "Past 1 Year": timedelta(days=365),
    "Past 2 Years": timedelta(days=730)
}

range_choice = st.sidebar.selectbox("Select Time Range", ["All"] + list(range_options.keys()), index=0)

if range_choice != "All":
    cutoff_date = date.today() - range_options[range_choice]
    filtered_df = filtered_df[filtered_df['timestamp'].dt.date >= cutoff_date]

# Subheader
st.subheader(f"Metrics for {group_choice} - {', '.join(player_choice)}")

metrics_to_plot = [
    "Speed_Max",
    "Jump Height(M)",
    "Peak Velocity(M/S)",
    "Peak Propulsive Power(W)",
    "Distance_Total"
]

for metric in metrics_to_plot:
    metric_df = filtered_df[filtered_df['metric'] == metric].copy()
    st.write(f"### {metric}")
    if metric_df.empty:
        st.write("No data available")
        continue

    metric_df['player_label'] = metric_df['playername'] + " (" + metric_df['groupteam'] + ")"

    line = (
        alt.Chart(metric_df)
        .mark_line(point=True)
        .encode(
            x=alt.X('timestamp:T', title='Timestamp'),
            y=alt.Y('value:Q', title='Value'),
            color=alt.Color('player_label:N', title='Player (Team)'),
            tooltip=[
                alt.Tooltip('timestamp:T', title='Timestamp'),
                alt.Tooltip('player_label:N', title='Player (Team)'),
                alt.Tooltip('value:Q', title='Value')
            ]
        )
    )

    trend = (
        alt.Chart(metric_df)
        .transform_regression('timestamp', 'value')
        .mark_line(color='yellow', size=2)
        .encode(
            x='timestamp:T',
            y='value:Q'
        )
        .properties(title="TREND")
    )

    chart = line + trend
    st.altair_chart(chart, use_container_width=True)
