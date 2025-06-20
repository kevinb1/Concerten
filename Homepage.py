import pandas as pd
import numpy as np
import copy
import streamlit as st
import altair as alt
import plotly.express as px
import datetime as dt

from functions import load_data, edit_data


##################################################################
#### Page configuration ####
##################################################################
st.set_page_config(
    page_title="Concerts Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

##################################################################
#### Session state ####
##################################################################
if "my_input" not in st.session_state:
    st.session_state["my_input"] = ""

##################################################################
####Load Data####
##################################################################
df_concerts = load_data("Concerts.xlsx", sheet_name=0)
df_collectables = load_data("Collectables.xlsx", sheet_name=0)

##################################################################
####Sidebar###
##################################################################
with st.sidebar:
    st.success("Select a Page Above")
    
    st.header("Filters")
    
    # Filter Band
    band = st.multiselect("Band",
                            options=df_concerts.Band.unique())
    
    # Filter Venue
    venue = st.multiselect("Venue",
                            options=df_concerts.Venue.unique())
    
    # Filter City
    city = st.multiselect("City",
                            options=df_concerts.City.unique())
    
    # Filter Date
    start_date = st.date_input("Start Date", 
                               value=None, 
                               min_value=min(df_concerts.Date), 
                               max_value=max(df_concerts.Date))
    end_date = st.date_input("End Date", 
                             value=None, 
                             min_value=min(df_concerts.Date), 
                             max_value=max(df_concerts.Date))

##################################################################
###Filter###
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
    df_concerts_selected = df_concerts.query(query_string)
    df_collectables_selected = df_collectables.query(query_string)
else:
    df_concerts_selected = df_concerts
    df_collectables_selected = df_collectables

##################################################################
####Homepage###
##################################################################
st.title("Data Used")

# Show data
colA1, colA2 = st.columns(2)
colA1.header("Visited Concerts")
colA1.data_editor(df_concerts_selected, use_container_width=True, hide_index=True, key="visited_concerts")

colA2.header("Collectables")
colA2.data_editor(df_collectables_selected, use_container_width=True, hide_index=True, key="collectables")


# Create option to edit databases
st.title("Edit Data")
colB1, colB2 = st.columns(2)
selected_table = colB1.radio("Select Table",
                            ["Visited Concerts", "Collectables"])

edit_type = colB2.radio("Add or Delete Instance",
                       ["Add", "Delete"])

# Adjust fielst do selection
if selected_table == "Visited Concerts":
    if edit_type == "Add":
        st.header(f"Add to {selected_table}")
        colC1, colC2, colC3, colC4, colC5, colC6 = st.columns(6)
        
        new_bands = colC1.text_input("Bands Seen")
        new_date = colC2.text_input("Date")
        new_venue = colC3.text_input("Venue")
        new_city = colC4.text_input("City")
        new_price = colC5.text_input("Price")
        new_headliner = colC6.radio("Headliner", ["Yes", "No"])
        
        edit_input = {"Band": new_bands, 
                      "Date": new_date,
                      "Venue": new_venue,
                      "City": new_city,
                      "Price": new_price,
                      "Headliner": new_headliner}
        
    else:
        st.header(f"Delete from {selected_table}")
        # Eddit_type == "Delete"
        colC1, colC2 = st.columns(2)
        
        delete_bands = colC1.text_input("Bands to Delete")
        delete_date = colC2.text_input("Date")
        
        edit_input = {"Band": delete_bands,
                      "Date": delete_date}
else:
    # Selected_tavle == Collectables
    if edit_type == "Add":
        st.header(f"Add to {selected_table}")
        colC1, colC2, colC3, colC4, colC5 = st.columns(5)
        
        new_collectable = colC1.text_input("Collectable")
        new_belongsto = colC2.text_input("Belongs To")
        new_band = colC3.text_input("Band")
        new_date = colC4.text_input("Date")
        new_venue = colC5.text_input("Venue")
        
        edit_input = {"Collectable": new_collectable, 
                      "BelongsTo": new_belongsto, 
                      "Band": new_band, 
                      "Date":new_date, 
                      "Venue": new_venue}
        
    else:
        # Eddit_type == "Delete"
        st.header(f"Delete from {selected_table}")
        
        colC1, colC2, colC3 = st.columns(3)
        
        delete_collectable= colC1.text_input("Collectable to Delete")
        delete_belongsto = colC2.text_input("Belongs To")
        delete_date = colC3.text_input("Date")
        
        edit_input = {"Collectable": delete_collectable,
                      "BelongsTo": delete_belongsto,
                      "Date": delete_date}

if st.button(f"Aply Changes", type="primary"):
    if selected_table == "Visited Concerts":
        df_concerts_edited = edit_data(df_concerts_selected, edit_type, edit_input)
        df_concerts_edited.to_excel("Concerts.xlsx", index=False)
    else:
        df_collectables_edited = edit_data(df_collectables_selected, edit_type, edit_input)
        df_collectables_edited.to_excel("Collectables.xlsx", index=False)
        
        

    # st.experimental_rerun()
    st.rerun()





