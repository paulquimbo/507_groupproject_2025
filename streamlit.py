import streamlit as st
import pandas as pd
import altair as alt

# Cache data loading for performance
@st.cache_data
def load_data():
    df = pd.read_csv('raw/sixmetrics_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by="playername")
    return df





# Import dataframe
sbusports = load_data()
sbusports['timestamp'] = pd.to_datetime(sbusports['timestamp'])
sbusports = sbusports.sort_values(by="playername")


# Sidebar selection for groupteam
group_options = ["All"] + sorted(sbusports['groupteam'].unique().tolist())
group_choice = st.sidebar.selectbox("Select a Group Team", group_options, index=0)

team_df = sbusports if group_choice == "All" else sbusports[sbusports['groupteam'] == group_choice]

# --- NEW: Checkbox to toggle restricted player list ---
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

# --- FIXED FILTER LOGIC ---
if "All" in player_choice:
    if restrict_players:
        # "All" = only the 4 selected players
        filtered_df = team_df[team_df['playername'].isin(selected_players)]
    else:
        # "All" = all players in team_df
        filtered_df = team_df
else:
    filtered_df = team_df[team_df['playername'].isin(player_choice)]

# Sidebar year filter (buttons)
years = sorted(sbusports['timestamp'].dt.year.unique())
year_choice = st.sidebar.radio("Select Year", ["All"] + years, index=0)
if year_choice != "All":
    filtered_df = filtered_df[filtered_df['timestamp'].dt.year == year_choice]

st.subheader(f"Metrics for {group_choice} - {', '.join(player_choice)}")

metrics_to_plot = [
    "Speed_Max",
    "Jump Height(M)",
    "Peak Velocity(M/S)",
    "Peak Propulsive Power(W)",
    "Distance_Total"
]

for metric in metrics_to_plot:
    metric_df = filtered_df[filtered_df['metric'] == metric]
    st.write(f"### {metric}")
    if metric_df.empty:
        st.write("No data available")
        continue

    # Base line chart with player colors
    line = (
        alt.Chart(metric_df)
        .mark_line(point=True)
        .encode(
            x=alt.X('timestamp:T', title='Timestamp'),
            y=alt.Y('value:Q', title='Value'),
            color=alt.Color('playername:N', title='Player'),
            tooltip=[
                alt.Tooltip('timestamp:T', title='Timestamp'),
                alt.Tooltip('playername:N', title='Player'),
                alt.Tooltip('value:Q', title='Value')
            ]
        )
    )

    # Trend line with fixed color and label "TREND"
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