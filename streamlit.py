# --- Add combined label column ---
sbusports['player_label'] = sbusports['playername'] + " (" + sbusports['groupteam'] + ")"

# Make sure filtered_df also carries this column
if "All" in player_choice:
    if restrict_players:
        filtered_df = team_df[team_df['playername'].isin(selected_players)]
    else:
        filtered_df = team_df
else:
    filtered_df = team_df[team_df['playername'].isin(player_choice)]

# Sidebar year filter
years = sorted(sbusports['timestamp'].dt.year.unique())
year_choice = st.sidebar.radio("Select Year", ["All"] + years, index=0)
if year_choice != "All":
    filtered_df = filtered_df[filtered_df['timestamp'].dt.year == year_choice]

# Update subheader to show combined labels
chosen_labels = filtered_df['player_label'].unique().tolist()
st.subheader(f"Metrics for {group_choice} - {', '.join(chosen_labels)}")

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

    # Base line chart with player+team labels
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

    # Trend line
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
