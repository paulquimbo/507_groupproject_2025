# --- Add combined label column for display only ---
sbusports['player_label'] = sbusports['playername'] + " (" + sbusports['groupteam'] + ")"

# ... your filtering logic stays exactly the same ...

for metric in metrics_to_plot:
    metric_df = filtered_df[filtered_df['metric'] == metric].copy()
    st.write(f"### {metric}")
    if metric_df.empty:
        st.write("No data available")
        continue

    # IMPORTANT: add the combined label to the filtered dataframe too
    metric_df['player_label'] = metric_df['playername'] + " (" + metric_df['groupteam'] + ")"

    # Base line chart with player+team labels
    line = (
        alt.Chart(metric_df)
        .mark_line(point=True)
        .encode(
            x=alt.X('timestamp:T', title='Timestamp'),
            y=alt.Y('value:Q', title='Value'),
            color=alt.Color('player_label:N', title='Player (Team)'),   # <-- use label
            tooltip=[
                alt.Tooltip('timestamp:T', title='Timestamp'),
                alt.Tooltip('player_label:N', title='Player (Team)'),   # <-- use label
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
