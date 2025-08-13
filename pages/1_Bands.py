import pandas as pd
import numpy as np
import copy
import streamlit as st
import matplotlib.pyplot as plt

from functions import load_data

##################################################################
#### Configuration###
##################################################################

st.set_page_config(
    page_title="Concerts Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

df_concerts_shown = load_data("Concerts.xlsx", sheet_name=0)
df_collectables_shown = load_data("Collectables.xlsx", sheet_name=0)

##################################################################
#### Sidebar###
##################################################################
with st.sidebar:
    st.success("Select a Page Above")
    st.header("Filters")

    # Band filter and metric
    col1, col2 = st.columns([2, 1])
    band = col1.multiselect("Band", options=df_concerts_shown.Band.unique())
    col2.metric("Bands", len(df_concerts_shown[df_concerts_shown["Band"].isin(
        band)]["Band"].unique()) if band else len(df_concerts_shown["Band"].unique()))

    # Venue filter and metric
    col1, col2 = st.columns([2, 1])
    venue = col1.multiselect("Venue", options=df_concerts_shown.Venue.unique())
    col2.metric("Venues", len(df_concerts_shown[df_concerts_shown["Venue"].isin(
        venue)]["Venue"].unique()) if venue else len(df_concerts_shown["Venue"].unique()))

    # City filter and metric
    col1, col2 = st.columns([2, 1])
    city = col1.multiselect("City", options=df_concerts_shown.City.unique())
    col2.metric("Cities", len(df_concerts_shown[df_concerts_shown["City"].isin(
        city)]["City"].unique()) if city else len(df_concerts_shown["City"].unique()))

    # Date filter (optional: no metric here)
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", value=None,
                                 min_value=min(df_concerts_shown.Date),
                                 max_value=max(df_concerts_shown.Date))
    end_date = col2.date_input("End Date", value=None,
                               min_value=min(df_concerts_shown.Date),
                               max_value=max(df_concerts_shown.Date))
##################################################################
### Filter###
##################################################################
# Apply filters
query_parts = []

if band:
    query_parts.append("Band in @band")
if venue:
    query_parts.append("Venue in @venue")
if city:
    query_parts.append("City in @city")
if start_date and end_date:
    query_parts.append(f"Date >= @start_date and Date <= @end_date")

query_string = " & ".join(query_parts)

# Apply the query if there are any filters, otherwise show the original dataframe
if query_string:
    df_concerts_shown = df_concerts_shown.query(query_string)
    df_collectables_shown = df_collectables_shown.query(query_string)
else:
    df_concerts_shown = df_concerts_shown
    df_collectables_shown = df_collectables_shown

##################################################################
#### Title###
##################################################################
st.title("Bands Statistics")


##################################################################
#### Basic statistics###
##################################################################
st.header("Selected Values")
# Display the metrics in columns
col1, col2, col3 = st.columns(3)

# Metrics for most/least seen
col1, col2 = st.columns(2)
# Most seen band
freq_table_Band = df_concerts_shown.value_counts(
    subset=['Band', 'Headliner']).reset_index(name='count')

# Get total count

# Calculate total count for each 'Band'
total_counts = freq_table_Band.groupby('Band')['count'].sum().reset_index()

# Merge total_counts back into counts DataFrame
freq_table_Band = freq_table_Band.merge(
    total_counts, on='Band', suffixes=('', '_total'))


# Sort the data by count
freq_table_Band_sorted = freq_table_Band.sort_values(
    ['count_total', "Band"], ascending=False)


mode_most = freq_table_Band["count_total"].max()
most_seen = sorted(list(
    freq_table_Band.loc[freq_table_Band["count_total"] == mode_most].Band.unique()))
most_seen_str = f"{', '.join(map(str, most_seen[:-1]))}{' & ' if len(most_seen) > 1 else ''}{most_seen[-1]}"

with st.container():
    col1.header("Most Seen Bands")
    col1.write(most_seen_str)

with st.container():
    col2.header("Times Seen")
    col2.subheader(f"{mode_most}")

##################################################################
#### Chart for bands seed###
##################################################################
st.dataframe(df_concerts_shown)
