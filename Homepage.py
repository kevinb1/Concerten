import pandas as pd
import numpy as np
import copy
import streamlit as st
import datetime as dt
import time
from streamlit_gsheets import GSheetsConnection




##################################################################
#### Page configuration ####
##################################################################
st.set_page_config(
    page_title="Concerts Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

##################################################################
#### Session state ####
##################################################################
if "my_input" not in st.session_state:
    st.session_state["my_input"] = ""

##################################################################
#### Load Data from database ####
##################################################################


conn = st.connection("gsheets", type=GSheetsConnection)
df_bands = conn.read(worksheet="dimBand")
df_dates = conn.read(worksheet="dimDate")
df_venues = conn.read(worksheet="dimVenue")
df_concerts = conn.read(worksheet="factConcert")
df_collectables = conn.read(worksheet="factCollectable")

# st.dataframe(df)





# st.experimental_rerun()
# st.rerun()
