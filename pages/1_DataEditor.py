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
    page_title="Data Editor",
    layout="wide",
    initial_sidebar_state="expanded")


##################################################################
#### Session state ####
##################################################################
# Update data
conn = update_connection()

if "sheet_names" not in st.session_state:
    sheet_names = [
        "dimBand",
        "dimVenue",
        "dimDate",
        "factConcert",
        "factCollectable"
        ]
    st.session_state["sheet_names"] = sheet_names

# Prompt for new venue
st.session_state['new_venue_prompt'] = False

##################################################################
# Authentication check
##################################################################
if not st.session_state.get("authentication_status"):
    st.warning("Please login to access the Data Editor page.")
    st.stop()
        

##################################################################
# Side bar
##################################################################
with st.sidebar:
    # Select table to show
    rad_df = st.radio(
        "Select table to show:",
        options=st.session_state["sheet_names"]
        )
    
    btn_refresh = st.button("Refresh Data",type="primary")
    st.link_button("Go to Google Sheets", url="https://docs.google.com/spreadsheets/d/1AHoEOXrxXaQhDkOjGsTo_85f2fJIgUDglvaBwBevMFE/edit?gid=0#gid=0")

    if btn_refresh:
        st.cache_data.clear()
        st.rerun()

        
##################################################################
# display data preview
##################################################################

conn = update_connection()
st.title(f"Selected table preview: {rad_df}")
df_bands = return_table(conn, "dimBand")
df_venues = return_table(conn, "dimVenue")
df_dates = return_table(conn, "dimDate")
df_concerts = return_table(conn, "factConcert")
df_collectables = return_table(conn, "factCollectable")


if rad_df == "dimBand":
    st.data_editor(df_bands, width="stretch")
elif rad_df == "dimVenue":
    st.data_editor(df_venues, width="stretch")
elif rad_df == "dimDate":
    st.data_editor(df_dates, width="stretch")
elif rad_df == "factConcert":
    st.data_editor(df_concerts, width="stretch")
elif rad_df == "factCollectable":
    st.data_editor(df_collectables, width="stretch")
else:
    st.write("Select a table to display.")

##################################################################
# data editor
##################################################################
st.title("Data Editor")
col1, col2 = st.columns(2)
rad_edit_type = col1.radio(
    "Select edit type:",
    options=[
        "Add Data",
        "Delete Data"
        ],
    horizontal=True
    )

rad_select_table = col2.radio(
    "Select facts table:",
    options=[
        "factConcert",
        "factCollectable"
        ],
    horizontal=True
    )

# Add DataEditor functionality
if rad_select_table == "factConcert":
    # Concerts selected
    if rad_edit_type == "Add Data":
        # Add data

        # Create input fields
        cols = st.columns(5)
        date_to_add = cols[0].date_input(
            "Select Date:",
            min_value=df_dates.Date.min(),
            max_value=dt.date.today(),
            value=dt.date.today()
            )
        
        band_to_add= cols[1].multiselect(
            "Select Bands to add concert for:",
            options=df_bands.Name.unique(),
            accept_new_options=True,
            )  
        
        venue_to_add= cols[2].selectbox(
            "Select Venue to add concert for:",
            options=df_venues.Venue.unique(),
            accept_new_options=True,
            index=None,
            ) 
        
        headliner_to_add= cols[3].selectbox(
            "Select Headliner to add concert for:",
            options=band_to_add,
            accept_new_options=False,
            )
        
        price_to_add= cols[4].number_input(
            "Select Price to add concert for:",
            min_value=0.0,
            value=50.00,
            step=0.01,
            format="%.2f"
            )


        # Input for city outside the button click block
        if venue_to_add not in df_venues.Venue.values and venue_to_add:
            st.session_state['new_venue_prompt'] = True
            city_to_add = st.text_input(f"Enter city for new venue '{venue_to_add}':")
            
            if len(city_to_add) >0:
                st.session_state['new_venue_prompt'] = False
        else:
            st.session_state['new_venue_prompt'] = False
            city_to_add = None
            
        # Add button
        btn_add = st.button("Add concert to database", 
                            type="primary", 
                            disabled=st.session_state["new_venue_prompt"])

        if btn_add:
            refresh = 0
            
            # Add new bands
            for band in band_to_add:
                if band not in df_bands.Name.values:
                    refresh += 1
                    new_band_id = new_id(df_bands.BandID)
                    new_band_row = pd.DataFrame({
                        "BandID": [new_band_id],
                        "Name": [band]
                    })
                    updated_data = pd.concat([df_bands, new_band_row], ignore_index=True)
                    conn.update(data=updated_data, worksheet="dimBand")
            
            # Add new venue (only if city is entered)
            if venue_to_add not in df_venues.Venue.values and city_to_add:
                refresh += 1
                new_venue_id = new_id(df_venues.VenueID)
                location_str = venue_to_add + ", " + city_to_add
                
                try:  
                    lon, lat = get_location(location_str)
                    lon = str(lon).replace(".", ",")
                    lat = str(lat).replace(".", ",")
                except TypeError:
                    lon, lat = None, None
                    
                new_venue_row = pd.DataFrame({
                    "VenueID": [new_venue_id],
                    "Venue": [venue_to_add],
                    "City": [city_to_add],
                    "Longitude": [lon],
                    "Latitude": [lat]
                })
                updated_data = pd.concat([df_venues, new_venue_row], ignore_index=True)
                conn.update(data=updated_data, worksheet="dimVenue")
            
            # Show warning only if something was added
            if refresh > 0:
                st.warning("New dimension data added. Please refresh the data connection.")
                st.cache_data.clear()
                st.rerun()
            
            row_to_add = pd.DataFrame({
                "Date": [date_to_add],  # wrap scalar in list
                "Price": [price_to_add],
                "Headliner": [return_id_from_dim(update_connection(), "dimBand", "Name", headliner_to_add)][0],
                "BandID": [return_id_from_dim(update_connection(), "dimBand", "Name", band_to_add)],
                "VenueID": [return_id_from_dim(update_connection(), "dimVenue", "Venue", venue_to_add)[0]]
            })

            new_rows = add_to_GSheet(
                update_connection(), 
                "factConcert", 
                row_to_add
                )
            
            msg = st.success("Concert added successfully. Rereshing data...")
            time.sleep(2)
            st.cache_data.clear()
            st.rerun()

    else:
        # Delete data
        # Add dropdowns for Band, and date
        col1, col2 = st.columns(2)
        
        df_concerts_temp = pd.merge(left=df_concerts.copy(), right=df_bands.copy(), 
                            right_on="BandID", left_on="BandID", 
                            how="inner")
        
        band_to_delete = col1.selectbox(
            "Select Band to delete concert for:",
            options=df_concerts_temp.Name.unique(),
            accept_new_options=False,
            index=None,
            )        
        
        df_concerts_temp = querried_df(df_concerts_temp,
                                       Name=band_to_delete)

        date_to_delete = col2.selectbox(
                "Select date (Y-mm-dd) to delete concert for:",
                options=df_concerts_temp.Date.unique(),
                index=None,
                accept_new_options=False,
                )

        df_concerts_temp = querried_df(df_concerts_temp,
                                Date=date_to_delete)

        st.dataframe(df_concerts_temp)
        
        # Delete button
        btn_delete = st.button("Delete selected concert", type="primary")
        if btn_delete:
            # Delete selected concert from GSheet
            del_from_GSheet(update_connection(), "factCollectable", df_concerts_temp)
            msg = st.success("Collectable deleted successfully.")
            time.sleep(2)
            st.cache_data.clear()
            st.rerun()

            

    # Collectables selected
else:
    if rad_edit_type == "Add Data":
        # Create input fields
        cols = st.columns(5)
        date_to_add = cols[3].date_input(
            "Select Date:",
            min_value=df_dates.Date.min(),
            max_value=dt.date.today(),
            value=dt.date.today()
            )
        
        collectable_to_add= cols[0].selectbox(
            "Select Collectable:",
            options=df_collectables.Collectable.unique(),
            accept_new_options=True,
            )  
        
        owner_to_add= cols[1].selectbox(
            "Select Person/Band:",
            options=df_collectables.BelongsTo.unique(),
            accept_new_options=False,
            index=None,
            ) 
        
        band_to_add= cols[2].selectbox(
            "Select Band:",
            options=df_bands.Name.unique(),
            accept_new_options=False,
            )  
        
        venue_to_add= cols[4].selectbox(
            "Select venue:",
            options=df_venues.Venue.unique(),
            accept_new_options=False,
            )  
        
         # Add button
        btn_add = st.button("Add collectable to database", 
                            type="primary")

        # Button pressed
        if btn_add:
            new_collectable_row = pd.DataFrame({
                "Collectable": [collectable_to_add],
                "BelongsTo": [owner_to_add],
                "Date": [date_to_add],
                "BandID": return_id_from_dim(update_connection(), "dimBand", "Name", band_to_add),
                "VenueID": return_id_from_dim(update_connection(), "dimVenue", "Venue", venue_to_add),
                "CollectableID": new_id(df_collectables.CollectableID)
            })
            
            # Check if all fields filled in
            if None in new_collectable_row:
                st.error("One of the fields is empty. Please fill in all fields.")
            else:

                updated_data = pd.concat([df_collectables, new_collectable_row], ignore_index=True)
                conn.update(data=updated_data, worksheet="factCollectable")
    
                msg = st.success("Collectable added successfully. Rereshing data...")
                time.sleep(2)
                st.cache_data.clear()
                st.rerun()


    else:
        # Delete data
        # Add dropdowns for collectable, owner, band, date,
        cols = st.columns(4)
        
        # Merge Bands and venues
        df_collectables_temp = pd.merge(left=df_collectables.copy(), right=df_bands.copy(), 
                            right_on="BandID", left_on="BandID", 
                            how="inner")
        
        
        collectable_to_delete = cols[0].selectbox(
            "Select Collectable to delete:",
            options=df_collectables_temp.Collectable.unique(),
            accept_new_options=False,
            index=None,
            )        
        
        df_collectables_temp = querried_df(df_collectables_temp,
                                       Collectable=collectable_to_delete)
        
        owner_to_delete = cols[1].selectbox(
            "Select Owner :",
            options=df_collectables_temp.BelongsTo.unique(),
            accept_new_options=False,
            index=None,
            )        
        
        df_collectables_temp = querried_df(df_collectables_temp,
                                       BelongsTo=owner_to_delete)
        
        band_to_delete = cols[2].selectbox(
            "Select Band:",
            options=df_collectables_temp.Name.unique(),
            accept_new_options=False,
            index=None,
            )        
        
        df_collectables_temp = querried_df(df_collectables_temp,
                                       Name=band_to_delete)
        
        date_to_delte = cols[3].selectbox(
            "Select Date :",
            options=df_collectables_temp.Date.unique(),
            accept_new_options=False,
            index=None,
            )        
        
        df_collectables_temp = querried_df(df_collectables_temp,
                                       Date=date_to_delte)


        st.dataframe(df_collectables_temp)
        
        # Delete button
        btn_delete = st.button("Delete selected Collectable", type="primary")
        if btn_delete:
            # Delete selected concert from GSheet
            del_from_GSheet(update_connection(), "factCollectable", df_collectables_temp)
            msg = st.success("Collectable deleted successfully.")
            time.sleep(2)
            st.cache_data.clear()
            st.rerun()



