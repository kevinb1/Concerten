import pandas as pd
import numpy as np
import copy
import streamlit as st
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import matplotlib.pyplot as plt


from functions import load_data, join_bands


st.set_page_config(
    page_title="Concerts Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")


df_concerts = load_data("Concerts.xlsx", sheet_name=0)
df_collectables = load_data("Collectables.xlsx", sheet_name=0)

df_events = df_concerts.groupby('Date').agg(
    Date=('Date', 'first'),
    Lineup=('Band', lambda x: join_bands(x, df_concerts.loc[x.index, 'Headliner'])),  # Join band names with headliner priority
    Venue=('Venue', 'first'),           # Take the first venue
    City=('City', 'first'),             # Take the first city
    Price=('Price', 'first')              # Sum the prices
).reset_index(drop=True)

# st.write(df_events)



####Sidebar###
with st.sidebar:
    st.header("Filters")
    
    # # Filter band
    band = st.multiselect("Band",
                            options=df_events.Lineup.str.split(', ').explode().drop_duplicates().sort_values())
    
    # Construct regex pattern to search for exact matches of each band followed by a comma
    pattern = '|'.join([f'\\b{a}\\b' for a in band])


    # Filter the DataFrame to find lineups containing any of the input bands followed by a comma
    i_lineup = df_events[df_events['Lineup'].str.contains(pattern)].index
    
    # Filter Venue
    venue = st.multiselect("Venue",
                            options=df_events.Venue.drop_duplicates().sort_values())
    
    # Filter City
    city = st.multiselect("City",
                            options=df_events.City.drop_duplicates().sort_values())
    
    # Filter Date
    start_date = st.date_input("Start Date", value=None, min_value=min(df_events.Date), max_value=max(df_events.Date))
    end_date = st.date_input("End Date", value=None, min_value=min(df_events.Date), max_value=max(df_events.Date))
     

####Title###
st.title("Costs Statistics")


###Filter###
#Create filter lists
query_parts = []

#Apply filters
if band:
    query_parts.append("index in @i_lineup")
if venue:
    query_parts.append("Venue in @venue")
if city:
    query_parts.append("City in @city")
if start_date and end_date:
    query_parts.append(f"Date >= @start_date and Date <= @end_date")

query_string = " & ".join(query_parts)

# Apply the query if there are any filters, otherwise show the original dataframe
if query_string:
    df_selection = df_events.query(query_string)
else:
    df_selection = df_events

st.header("Selected Values")
# Display the metrics in columns
col1, col2, col3 = st.columns(3, gap="small")

# Bands selected
with st.container():
    col1.metric("Events Selected", len(df_selection['Lineup'].unique()))
    col1.write(f"Of {len(df_events['Lineup'].unique())}")

# Venues selected
with st.container():
    col2.metric("Venues Selected", len(df_selection['Venue'].unique()))
    col2.write(f"Of {len(df_events['Venue'].unique())}")

# Cities selected
with st.container():
    col3.metric("Cities Selected", len(df_selection['City'].unique()))
    col3.write(f"Of {len(df_events['City'].unique())}")


### Dashboard ###