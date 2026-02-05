import pandas as pd
import numpy as np
import copy
import streamlit as st
import datetime as dt
import time
from streamlit_gsheets import GSheetsConnection
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
import random as rd
import plotly.express as px

from functions import return_table, querried_df, new_id, del_from_GSheet, update_connection, add_to_GSheet, \
return_id_from_dim, get_location

##################################################################
#Page configuration 
##################################################################
st.set_page_config(
    page_title="Venue Statistics",
    layout="wide",
    initial_sidebar_state="expanded")


##################################################################
#### Session state ####
##################################################################
# Update data
conn = update_connection()

# Load data
df_bands = return_table(conn, "dimBand")
df_venues = return_table(conn, "dimVenue")
df_dates = return_table(conn, "dimDate")
df_dates['Date'] = pd.to_datetime(df_dates['Date'], format="%Y-%m-%d")

df_concerts = return_table(conn, "factConcert")
df_concerts['Date'] = pd.to_datetime(df_concerts['Date'], format="%Y-%m-%d")

df_collectables = return_table(conn, "factCollectable")


##################################################################
# Side bar
##################################################################
with st.sidebar:
    st.title("Filter Panel")
    
    # Reset filters button
    default_dates = (df_dates.Date.min(), df_dates.Date.max())
    reset_filters = st.button("Reset filters", use_container_width=True, type="primary")
    if reset_filters:
        st.rerun()
    
    # Date filters
    start_date_filter = st.date_input("Select start date:",
                                      value=min(default_dates),
                                      min_value=df_dates.Date.min(),
                                      max_value=df_dates.Date.max()
                                      )

    end_date_filter = st.date_input("Select end date:",
                                    value=max(default_dates),
                                    min_value=df_dates.Date.min(),
                                    max_value=df_dates.Date.max()
                                    )
    
    
    df_dates_filtered = querried_df(df_dates, 
                                    Date=lambda x: (x >= pd.to_datetime(start_date_filter)) & \
                                        (x <= pd.to_datetime(end_date_filter)))
    
    
    # Venue filter
    venue_filter = st.multiselect("Select venues:",
                                    options=df_venues.sort_values(by="Venue").Venue.unique(),
                                    default=None
                                    )
    
    df_venues_filtered = querried_df(df_venues, Venue=venue_filter) if venue_filter else df_venues
    
    # Filter facts using filterred dimensions
    df_concerts_filtered = df_concerts[df_concerts.Date.isin(df_dates_filtered.Date) & \
                                        df_concerts.VenueID.isin(df_venues_filtered.VenueID)]

##################################################################
# Venue statistics
##################################################################

# Title
st.title(f"{rd.choice(st.session_state['music_emojis'])} Venue Statistics {rd.choice(st.session_state['music_emojis'])}")

# KPI's for venues
top_row = st.columns(6)
SELECTEDYEAR = df_concerts_filtered.Date.dt.year.max()
first_time_visits = df_concerts.drop_duplicates(subset=['VenueID'], keep='first') 
first_time_visits_since_year = len(first_time_visits[first_time_visits['Date'].dt.year >= SELECTEDYEAR])

venues_ts = copy.deepcopy(df_concerts)
venues_ts = venues_ts.drop_duplicates(subset=['VenueID'], keep='first').reset_index()
venues_ts = venues_ts.groupby(venues_ts['Date'].dt.year).count()['VenueID'].cumsum()

top_row[0].metric(
    label="Number of venues visited", 
    value=df_concerts_filtered.VenueID.nunique(),
    delta=f"+{first_time_visits_since_year} in {SELECTEDYEAR}",
    border=True,
    chart_data= venues_ts,
    chart_type="bar",
    width="content"
    )

concerts_ts = copy.deepcopy(df_concerts)[["Date", "Price"]]
concerts_ts = concerts_ts.groupby(concerts_ts['Date'].dt.year).nunique()['Date']
concerts_since_year = concerts_ts[concerts_ts.index >= SELECTEDYEAR].sum()

top_row[1].metric(
    label="Total concerts attended",
    value=df_concerts_filtered.Date.nunique(),
    delta=f"+{first_time_visits_since_year} in {SELECTEDYEAR}",
    border=True,
    chart_data=concerts_ts,
    chart_type="bar",
    width="content"
)
# Map visuals
map_visuals = st.columns(2)

# Visited venues on map
map_visuals[0].header("Venues visited")
concerts_grouped = df_concerts_filtered.drop_duplicates(subset=["Date"], keep="first")
concerts_grouped = concerts_grouped.groupby("VenueID").agg(count=("ConcertID", "count")).reset_index()
concerts_grouped = concerts_grouped.merge(df_venues_filtered, left_on='VenueID', right_on='VenueID', how='left')
concerts_grouped["marker_size"] = concerts_grouped["count"] * 200
concerts_grouped.sort_values(by="Venue", ascending=True, inplace=True)

# st.write(concerts_grouped)


# Create Plotly map object
fix_venues = px.scatter_map(
    concerts_grouped,
    lat="Latitude",
    lon="Longitude",
    size="marker_size",
    color="Venue",                 
    hover_name="Venue",
    hover_data={
        "count": True,
        "City": True,
        "Latitude": False,
        "Longitude": False,
        "marker_size": False
    },
    color_discrete_sequence=px.colors.qualitative.Set2,
    zoom=6
)

fix_venues.update_layout(
    mapbox_style="carto-darkmatter",
    height=600, 
    paper_bgcolor="black",
    font=dict(color="white"),
    legend_title_text="Venue",
    margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(
        title="Venues",
        font=dict(size=18),
        title_font=dict(size=20)
    )
)
fix_venues.update_traces(
    hovertemplate=
    "<b>%{hovertext}</b><br>" +
    "City: %{customdata[1]}<br>" +
    "Concerts: %{customdata[0]}<br>" +
    "<extra></extra>"
)

# Show visual
map_visuals[0].plotly_chart(fix_venues, theme="streamlit")

