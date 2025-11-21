import streamlit as st
import pandas as pd
import altair as alt

# Import dataframe
sbusports = pd.read_csv('raw/sixmetricsclass.csv')
sbusports['timestamp'] = pd.to_datetime(sbusports['timestamp'])

# Sidebar selection for groupteam
group_options = ["All"] + sbusports['groupteam'].unique().tolist()
group_choice = st.sidebar.selectbox("Select a Group Team", group_options, index=0)

team_df = sbusports if group_choice == "All" else sbusports[sbusports['groupteam'] == group_choice]

# --- NEW: Checkbox to toggle restricted player list ---
restrict_players = st.sidebar.checkbox("Restrict to selected players", value=False)

# Define your 4 selected players (replace with actual names or logic)
selected_players = ["PlayerA", "PlayerB", "PlayerC", "PlayerD"]

if restrict_players:
    # Only show "All" + the 4 selected players
    player_options = ["All"] + [p for p in selected_players if p in team_df['playername'].unique()]
else:
    # Show "All" + all players
    player_options = ["All"] + team_df['playername'].unique().tolist()

# Sidebar selection for playername (multi-select)
player_choice = st.sidebar.multiselect("Select Player(s)", player_options, default=["All"])

# Filter dataframe
filtered_df = team_df if "All" in player_choice else team_df[team_df['playername'].isin(player_choice)]

# Sidebar year filter (buttons)
years = sorted(sbusports['timestamp'].dt.year.unique())
year_choice = st.sidebar.radio("Select Year", ["All"] + years, index=0)
if year_choice != "All":
    filtered_df = filtered_df[filtered_df['timestamp'].dt.year == year_choice]

st.subheader(f"Metrics for {group_choice} - {', '.join(player_choice)}")

metrics_to_plot = [
    "Speed_Max",
    "Jump Height(M)",
    "Mrsi",
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
        .mark_line(color='red', size=3)
        .encode(
            x='timestamp:T',
            y='value:Q'
        )
        .properties(title="TREND")
    )

    chart = line + trend
    st.altair_chart(chart, use_container_width=True)