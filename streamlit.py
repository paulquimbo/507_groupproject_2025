import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta

# --- Page config to remove huge left space ---
st.set_page_config(
    page_title="Sports Metrics Dashboard",
    layout="wide"   # <-- makes charts span full width, no big gutter
)

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

# Checkbox to toggle restricted player list (always checked initially)
restrict_players = st.sidebar.checkbox("Check Box for Selected Players", value=True)

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

# --- NEW: Toggle for aggregated vs individual views ---
agg_view = st.sidebar.checkbox("Show Aggregated View (Mean by GroupTeam)", value=False)

for metric in metrics_to_plot:
    metric_df = filtered_df[filtered_df['metric'] == metric].copy()
    st.write(f"### {metric}")
    if metric_df.empty:
        st.write("No data available")
        continue

    metric_df['player_label'] = metric_df['playername'] + " (" + metric_df['groupteam'] + ")"

    if agg_view:
        # Aggregated mean profiles by groupteam
        agg_df = (
            metric_df.groupby(['groupteam', 'timestamp'], as_index=False)
            .agg({'value': 'mean'})
        )
        chart = (
            alt.Chart(agg_df)
            .mark_line(point=True)
            .encode(
                x=alt.X('timestamp:T', title='Timestamp'),
                y=alt.Y('value:Q', title='Mean Value'),
                color=alt.Color('groupteam:N', title='Group Team'),
                tooltip=['timestamp:T', 'groupteam:N', 'value:Q']
            )
        )
    else:
        # Faceted charts per player to reduce clutter
        line = (
            alt.Chart(metric_df)
            .mark_line(point=True)
            .encode(
                x=alt.X('timestamp:T', title='Timestamp'),
                y=alt.Y('value:Q', title='Value'),
                color=alt.Color('player_label:N', title='Player (Team)'),
                tooltip=['timestamp:T', 'player_label:N', 'value:Q']
            )
        )

        trend = (
            alt.Chart(metric_df)
            .transform_regression('timestamp', 'value')
            .mark_line(color='yellow', size=2)
            .encode(x='timestamp:T', y='value:Q')
            .properties(title="TREND")
        )

        chart = (line + trend).facet(
            column='player_label:N'
        )

    st.altair_chart(chart, use_container_width=True)

# --- NEW SECTION: Comparison of Player Mean vs GroupTeam Mean ---
st.subheader("Comparison: Player Mean vs GroupTeam Mean")

for metric in metrics_to_plot:
    metric_df = filtered_df[filtered_df['metric'] == metric].copy()
    if metric_df.empty:
        st.write(f"No data available for {metric}")
        continue

    # Player mean (based on current filters)
    player_means = (
        metric_df.groupby(['playername', 'groupteam'], as_index=False)
        .agg({'value': 'mean'})
        .rename(columns={'value': 'player_mean'})
    )

    # GroupTeam mean (based on current filters)
    group_means = (
        metric_df.groupby('groupteam', as_index=False)
        .agg({'value': 'mean'})
        .rename(columns={'value': 'group_mean'})
    )

    # Merge player mean with group mean
    comparison_df = pd.merge(player_means, group_means, on='groupteam')

    # Melt for Altair grouped bar chart
    comparison_melt = comparison_df.melt(
        id_vars=['playername', 'groupteam'],
        value_vars=['player_mean', 'group_mean'],
        var_name='Type',
        value_name='MeanValue'
    )

    # Label players with team
    comparison_melt['player_label'] = comparison_melt['playername'] + " (" + comparison_melt['groupteam'] + ")"

    st.write(f"### {metric} Mean Comparison")

    chart = (
        alt.Chart(comparison_melt, width=1000)  # wider chart for long labels
        .mark_bar()
        .encode(
            x=alt.X('player_label:N', title='Player (Team)', axis=alt.Axis(labelAngle=0)),  # horizontal labels
            xOffset='Type:N',  # side-by-side bars per player
            y=alt.Y('MeanValue:Q', title='Mean Value'),
            color=alt.Color('Type:N', title='Mean Type', scale=alt.Scale(scheme='set2')),
            tooltip=['player_label:N', 'Type:N', 'MeanValue:Q']
        )
    )

    st.altair_chart(chart, use_container_width=True)
