import pandas as pd
import numpy as np
import copy
import streamlit as st
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import matplotlib.pyplot as plt

from functions import load_data

##################################################################
####Configuration###
##################################################################

st.set_page_config(
    page_title="Concerts Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

df_concerts = load_data("Concerts.xlsx", sheet_name=0)
df_collectables = load_data("Collectables.xlsx", sheet_name=0)

##################################################################
####Sidebar###
##################################################################
with st.sidebar:
    st.header("Filters")
    
    # Filter Band
    band = st.multiselect("Band",
                            options=df_concerts.Band.drop_duplicates().sort_values())
    
    # Filter Venue
    venue = st.multiselect("Venue",
                            options=df_concerts.Venue.drop_duplicates().sort_values())
    
    # Filter City
    city = st.multiselect("City",
                            options=df_concerts.City.drop_duplicates().sort_values())
    
    # Filter Date
    start_date = st.date_input("Start Date", value=None, min_value=min(df_concerts.Date), max_value=max(df_concerts.Date))
    end_date = st.date_input("End Date", value=None, min_value=min(df_concerts.Date), max_value=max(df_concerts.Date))
     

##################################################################
####Title###
##################################################################
st.title("Bands Statistics")

##################################################################
####Filters###
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
    df_concerts_shown = df_concerts.query(query_string)
    df_collectables_shown = df_collectables.query(query_string)
else:
    df_concerts_shown = df_concerts
    df_collectables_shown = df_collectables

##################################################################
####Basic statistics###
##################################################################
st.header("Selected Values")
# Display the metrics in columns
col1, col2, col3 = st.columns(3)

# Bands selected
with st.container():
    col1.metric("Bands Selected", len(df_concerts_shown['Band'].unique()), border=True)
    col1.write(f"Of {len(df_concerts['Band'].unique())}")


# Venues selected
with st.container():
    col2.metric("Venues Selected", len(df_concerts_shown['Venue'].unique()), border=True)
    col2.write(f"Of {len(df_concerts['Venue'].unique())}")

# Cities selected
with st.container():
    col3.metric("Cities Selected", len(df_concerts_shown['City'].unique()), border=True)
    col3.write(f"Of {len(df_concerts['City'].unique())}")

# Metrics for most/least seen
col1, col2 = st.columns(2)
# Most seen band
freq_table_Band = df_concerts_shown.value_counts(subset=['Band', 'Headliner']).reset_index(name='count')

# Get total count

# Calculate total count for each 'Band'
total_counts = freq_table_Band.groupby('Band')['count'].sum().reset_index()

# Merge total_counts back into counts DataFrame
freq_table_Band = freq_table_Band.merge(total_counts, on='Band', suffixes=('', '_total'))


# Sort the data by count
freq_table_Band_sorted = freq_table_Band.sort_values(['count_total', "Band"], ascending=False)


mode_most = freq_table_Band["count_total"].max()
most_seen = sorted(list(freq_table_Band.loc[freq_table_Band["count_total"] == mode_most].Band.unique()))
most_seen_str = f"{', '.join(map(str, most_seen[:-1]))}{' & ' if len(most_seen) > 1 else ''}{most_seen[-1]}"

with st.container():
    col1.header("Most Seen Bands")
    col1.write(most_seen_str)

with st.container():
    col2.header("Times Seen")
    col2.subheader(f"{mode_most}")

##################################################################
####Chart for bands seed###
##################################################################

# Bar chart for frequency
st.header("Frequency Bar Chart")
st.markdown("""---""")
st.subheader("Chart Options")

# Filter on chart options
col1, col2 , col3 = st.columns(3)
with col1:
    display_n = st.number_input("Show Amount", min_value=1, max_value=len(df_concerts['Band'].unique()), value =20)

with col2:
    sort = st.radio("Choose to Display Top or Bottom", ["Top", "Bottom"])

with col3:
    seen_type = st.radio("Select Type", ["All", "Headliners", "Support"])
    
# Make copy
freq_table_Band_filtered =  freq_table_Band_sorted.copy()

# Selectt seen_type
if seen_type == "Headliners":
    freq_table_Band_filtered = freq_table_Band_filtered.loc[freq_table_Band_filtered["Headliner"] == 1]
    freq_table_Band_filtered = freq_table_Band_filtered.sort_values(["count", "Band"], ascending=False)
elif seen_type == "Support":
    freq_table_Band_filtered = freq_table_Band_filtered.loc[freq_table_Band_filtered["Headliner"] == 0]
    freq_table_Band_filtered = freq_table_Band_filtered.sort_values(["count", "Band"], ascending=False)
else:
    freq_table_Band_filtered = freq_table_Band_filtered.sort_values(["count_total", "Band"], ascending=False)

# Get desired top/bottom n
if sort == "Top":
    freq_table_Band_filtered = freq_table_Band_filtered.head(display_n).reset_index(drop=True)
else:
    freq_table_Band_filtered = freq_table_Band_filtered.tail(display_n).reset_index(drop=True)

# Crate bar for headliners
barchart = go.Figure()
barchart.add_trace(go.Bar(
    x=freq_table_Band_filtered.loc[freq_table_Band_filtered["Headliner"] == 1]['count'],
    y=freq_table_Band_filtered.loc[freq_table_Band_filtered["Headliner"] == 1]['Band'],
    orientation='h',
    text=freq_table_Band_filtered.loc[freq_table_Band_filtered["Headliner"] == 1]['count'],
    textposition=('inside'),
    textangle=0,
    textfont=dict(size=20),
    name='Headliner',
    marker=dict(color='blue'),
))

# Create bar for support
barchart.add_trace(go.Bar(
    x=freq_table_Band_filtered.loc[freq_table_Band_filtered["Headliner"] == 0]['count'],
    y=freq_table_Band_filtered.loc[freq_table_Band_filtered["Headliner"] == 0]['Band'],
    orientation='h',
    text=freq_table_Band_filtered.loc[freq_table_Band_filtered["Headliner"] == 0]['count'],
    textposition='inside',
    textangle=0,
    textfont=dict(size=20),
    name='Support',
    marker=dict(color='orange'),
))

# Add total count
for band in freq_table_Band_filtered['Band'].unique():
    total = freq_table_Band_filtered.loc[freq_table_Band_filtered['Band'] == band, 'count_total'].values[0]
    barchart.add_annotation(
    x=total,
    y=band,
    text=f"{total}",
    showarrow=False,
    font=dict(size=16),
    xanchor='left',
    yanchor='middle'
)

barchart.update_layout(barmode="stack")

band_order = freq_table_Band_filtered.sort_values(["count_total"], ascending=False)['Band'].tolist()
band_order= band_order[::-1]
barchart.update_layout(
    yaxis=dict(
        categoryorder='array',
        categoryarray=band_order
    )
)

barchart.update_layout(
    barmode="stack",
    height=30 * len(band_order),  # 30px per bar, adjust as needed
    yaxis=dict(
        categoryorder='array',
        categoryarray=band_order
    )
)
st.plotly_chart(barchart, use_container_width=True)