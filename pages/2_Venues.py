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


##################################################################
# Side bar
##################################################################
with st.sidebar:
    st.title("Filter Panel")


##################################################################
# Venue statistics
##################################################################
# Load data
df_bands = return_table(conn, "dimBand")
df_venues = return_table(conn, "dimVenue")
df_dates = return_table(conn, "dimDate")
df_dates['Date'] = pd.to_datetime(df_dates['Date'], format="%Y-%m-%d")

df_concerts = return_table(conn, "factConcert")
df_concerts['Date'] = pd.to_datetime(df_concerts['Date'], format="%Y-%m-%d")

df_collectables = return_table(conn, "factCollectable")

# Title
st.title(f"{rd.choice(st.session_state['music_emojis'])} Venue Statistics {rd.choice(st.session_state['music_emojis'])}")

# KPI's for venues
top_row = st.columns(2)
SELECTEDYEAR = 2025
first_time_visits = df_concerts.drop_duplicates(subset=['VenueID'], keep='first') 
first_time_visits_since_year = len(first_time_visits[first_time_visits['Date'].dt.year >= SELECTEDYEAR])

venues_ts = copy.deepcopy(df_concerts)
venues_ts = venues_ts.drop_duplicates(subset=['VenueID'], keep='first').reset_index()
venues_ts = venues_ts.groupby(venues_ts['Date'].dt.year).count()['VenueID'].cumsum()

top_row[0].metric(
    label="Number of venues visited", 
    value=df_concerts.VenueID.nunique(),
    delta=f"+{first_time_visits_since_year} since {SELECTEDYEAR}",
    border=True,
    chart_data= venues_ts,
    chart_type="bar",
    width="content"

    )