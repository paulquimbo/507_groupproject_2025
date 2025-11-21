import streamlit as st
import pandas as pd

# Import dataframe
sbusports = pd.read_csv('raw/sixmetricsclass.csv')

# Sidebar selection for groupteam
group_choice = st.sidebar.selectbox(
    "Select a Group Team",
    sbusports['groupteam'].unique()
)

# Filter dataframe based on groupteam
team_df = sbusports[sbusports['groupteam'] == group_choice]

# Sidebar selection for playername (filtered by groupteam)
player_choice = st.sidebar.selectbox(
    "Select a Player",
    team_df['playername'].unique()
)

# Filter dataframe based on playername
filtered_df = team_df[team_df['playername'] == player_choice]

st.subheader(f"Metrics for {group_choice} - {player_choice}")

# First graph: timestamp vs metric/value
st.line_chart(filtered_df, x='timestamp', y=['metric', 'value'])

# Second graph: metric vs classification
st.bar_chart(filtered_df, x='metric', y='classification')