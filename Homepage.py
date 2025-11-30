import pandas as pd
import numpy as np
import copy
import streamlit as st
import datetime as dt
import time
from streamlit_gsheets import GSheetsConnection
import random as rd


##################################################################
#Page configuration 
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

# Create data connection and add to session state
conn = st.connection("gsheets", type=GSheetsConnection)
st.session_state["conn"] = conn
    
# Add sheet names to session state
if "sheet_names" not in st.session_state:
    sheet_names = [
        "dimBand",
        "dimVenue",
        "dimDate",
        "factConcert",
        "factCollectable"
        ]
    st.session_state["sheet_names"] = sheet_names

# add emoji's to session state
music_emojis = [
    "🎵","🎶","♩","♪","♫","♬","♭","♯","♮","🎼","🎤","🎧","🔊""🎸","🎻","🪕","🪘","🥁","🎹","🎺",
    "🎷","🪗","🎙️","📻","🎚️","🎛️","💿","📀"
]
st.session_state["music_emojis"] = music_emojis


##################################################################
# Side bar
##################################################################
with st.sidebar:
    st.header("Navigation")
    st.write("""
    Use the menu at the top left to navigate through the different pages of the Concerts Dashboard app.
    """)
    
##################################################################
# Title page
##################################################################

st.title(f"{rd.choice(music_emojis)} Concerts Dashboard")

st.write("Vullen met dashboard dingen uit andere pages")






# st.experimental_rerun()
# st.rerun()
