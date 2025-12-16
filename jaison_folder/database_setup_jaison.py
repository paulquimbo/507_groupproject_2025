from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()  # automatically finds and loads the file


# mapping for database connection
# need to rename the username since it conflicts with a reserved word windows

sql_username = os.getenv('POWERUSER')
sql_password = os.getenv('PASSWORD')
sql_host = os.getenv('HOSTNAME')
sql_database = os.getenv('DATABASE')

# Creating the Database Connection URL & initializing the Database Engine
url = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"
engine = create_engine(url)

# Writing and Executing the SQL Query
query = "SELECT * FROM research_experiment_refactor_test;"
df = pd.read_sql(query, engine)
print(df.head(10))  # Display the first few rows of the dataframe

# For a random sample of 5000000 rows:
df = df.sample(n=5000000, random_state=42)  # random_state ensures reproducibility
print(df.head())



pd.set_option('display.max_columns', None)
print(df.info())  # Display the dataframe info
# ******************************************************************************



print(df['metric'])
  # Display statistical summary of the dataframe
# First, list all metric columns (numeric columns)
metric_columns = df.select_dtypes(include=['number']).columns.tolist()

# Get the top 10 most frequent metric values and their counts
top_10_metrics = df['metric'].value_counts().head(10)

print("Top 10 most common metrics and their counts:")
print(top_10_metrics)


metrics_to_check = [
    "Avg. Braking Force(N)",
    "Avg. Braking Power(W)",
    "Avg. Braking Velocity(m/s)",
    "Avg. Landing Force(N)",
    "Avg. Propulsive Force(N)"
]

for metric_name in metrics_to_check:
    count = df['metric'].value_counts().get(metric_name, 0)
    print(f"Count for '{metric_name}': {count}")

# *****************************************************************************

# Check for sports-related data in the dataframe
print(df.columns)
print(df['team'].unique())

# Example: Count occurrences of each team if there's a 'team' column
if 'team' in df.columns:
    print(df['team'].value_counts())

# *****************************************************************************

# Find the top 5 teams by frequency
top_5_teams = df['team'].value_counts().head(5).index.tolist()
print("Top 5 teams:", top_5_teams)

# For those teams, find the top 5 metrics used
from collections import Counter
metrics_counter = Counter()

# For each of the top teams, collect metrics
for team in top_5_teams:
    team_df = df[df['team'] == team]
    metrics_counter.update(team_df['metric'].value_counts().to_dict())

# Get the top 5 most common metrics across these teams
top_5_metrics = [item[0] for item in metrics_counter.most_common(5)]
print("Top 5 metrics used across the top 5 teams:", top_5_metrics)

analysis_df = df[(df['team'].isin(top_5_teams)) & (df['metric'].isin(top_5_metrics))]
print(analysis_df.head())


# *****************************************************************************

# Step 1: Select 5 Metrics Well-Represented Across Top Teams
# (Assume df is your DataFrame and 'team' and 'metric' are your columns)
top_5_teams = [
    "Football",
    "Mens Basketball",
    "Womens Basketball",
    "Womens Soccer",
    "Mens Soccer"
]

# Find all metrics represented in these teams (sorted by usage)
metrics_across_teams = (
    df[df['team'].isin(top_5_teams)]['metric']
    .value_counts()
)
print("Metrics ranked by frequency across top 5 teams:")
print(metrics_across_teams)

# Pick the top 5 most common metrics for literature review:
selected_metrics = metrics_across_teams.head(5).index.tolist()
print("Your 5 selected metrics:", selected_metrics)


# *****************************************************************************
# Step 2: For Each Metric, Pull Data (to Summarize, Plot, or Export for Literature Review)
for metric in selected_metrics:
    print(f"\n--- Summary for {metric} ---")
    metric_df = df[(df['metric'] == metric) & (df['team'].isin(top_5_teams))]
    print(metric_df.describe(include='all'))  # Stats summary
    # Optional: Show some rows as examples
    print(metric_df.head())
    # Plot distribution if you wish (requires matplotlib):
    # metric_df['value_column'].hist()
    # plt.title(metric)
    # plt.show()
# *****************************************************************************
# Step 3: Random Sampling Across the Dataset (for Bias-Free Analysis)

random_sample = df.sample(n=1000, random_state=42)  # 1000-row unbiased sample
print(random_sample.head())
# *****************************************************************************
# Step 4: For Gaps/Comparisons Across Sports and Metrics
# Produce a pivot table for cross-comparing selected metrics and teams:

pivot = (
    df[df['metric'].isin(selected_metrics) & df['team'].isin(top_5_teams)]
    .pivot_table(index='team', columns='metric', aggfunc='size', fill_value=0)
)
print(pivot)


#*****************************************************************************# Step 5: Focused Analysis on Specific Metrics of Interest


selected_metrics = [
    "Avg. Braking Velocity(m/s)",  # Use exact name/variation in your data!
    "Peak Landing Force(N)",
    "Landing Stiffness(N/m)",
    "Peak Propulsive Power(W)",
    "event_count_exertion_category4"  # Or exact spelling from your dataset!
]

analysis_df = df[df['metric'].isin(selected_metrics)]
print(analysis_df['metric'].value_counts())

# For summary statistics/review
for metric in selected_metrics:
    metric_df = analysis_df[analysis_df['metric'] == metric]
    print(f"\n--- Summary for {metric} ---")
    print(metric_df.describe(include="all"))
    # Optional: if metric value column exists
    # metric_df['value_column'].hist()

# *****************************************************************************
# Step 5: Create a DataFrame for Literature Review Purposes

data = {
    'Metric': [
        "Avg. Braking Velocity(m/s)", 
        "Peak Landing Force(N)", 
        "Landing Stiffness(N/m)", 
        "Peak Propulsive Power(W)", 
        "event_count_exertion_category4"
    ],
    'Why Important': [
        "Deceleration/agility/joint injury risk", 
        "Max load/landing injury & performance", 
        "Neuromuscular control/injury risk",
        "Explosive movements/jump/sprint performance", 
        "Athlete load/fatigue monitoring"
    ],
    'Literature Example': [
        "PMC6132493", 
        "PMC3784371, PMC4151830", 
        "PMC7735694, SciDirect Youth Soccer", 
        "Academia.edu Velocity-Power, SPSR105 Beattie", 
        "PMC5350460, PMC8817215"
    ],
    'Search Keywords': [
        "braking velocity biomechanics sports",
        "peak landing force ground reaction injury jump",
        "landing stiffness biomechanics ACL injury",
        "peak propulsive power sprint jump performance",
        "event count exertion wearable monitoring team sports"
    ]
    # add columns for Mean, Std, Min, Max, Count using your own dataset's values!
}

df_metrics = pd.DataFrame(data)
df_metrics.to_excel('selected_metrics_lit_review.xlsx', index=False)
#******************************************************************************
# Step 6: Summarize Selected Metrics by Team



import pandas as pd

selected_metrics = [
    "Peak Landing Force(N)",
    "Landing Stiffness(N/m)",
    "Peak Propulsive Power(W)",
    "Event Count Exertion",        # or adapt to your dataset e.g. "event_count_exertion_category4"
    "Avg. Braking Velocity(m/s)"
]

# Filter for selected metrics
filtered_df = df[df['metric'].isin(selected_metrics)]

# Basic summary statistics by team/metric
summary = (
    filtered_df
    .groupby(['team', 'metric'])['value']
    .agg(['mean', 'std', 'min', 'max', 'count'])
    .reset_index()
)

# Optional: Pivot table format (teams as rows, each metric's mean value as columns)
pivot = (
    filtered_df
    .groupby(['team', 'metric'])['value']
    .mean()
    .unstack()
)

print(summary)
print(pivot)
pivot.to_excel("team_metric_pivot.xlsx")
summary.to_excel("team_metric_summary_stats.xlsx")

# If you want wide format for reporting:
table = pd.pivot_table(filtered_df, values='value', index='team', columns='metric',
                       aggfunc=['mean', 'std', 'min', 'max', 'count'], fill_value='')

table.to_excel('team_metric_detail_table.xlsx')



