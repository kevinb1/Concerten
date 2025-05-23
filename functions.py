import pandas as pd
import numpy as np
from io import BytesIO
import streamlit as st
import openpyxl
import datetime as dt

def load_data(data, sheet_name):
    df = pd.read_excel(data, sheet_name=sheet_name)

    # Sort data by date
    df = df.sort_values(by="Date", axis=0)

    # Convert date column to date 
    df.Date = df.Date.dt.date
    
    # Sort and reset index
    df = df.sort_values(by="Date", ascending=False)
    df = df.reset_index(drop=True)
    
    return df
    
# def join_bands(bands):
#     return ', '.join(sorted(bands))
def join_bands(bands, headliners):
    # Create a list of tuples (band, headliner)
    band_headliner = list(zip(bands, headliners))
    # Sort by headliner (descending)
    band_headliner.sort(key=lambda x: x[1], reverse=True)
    # Join band names
    return ', '.join(band for band, headliner in band_headliner)
    

def edit_data(df, edit_type, input_values):
    try:
        input_values["Band"].strip.split(",")
    except:
        input_values["Collectable"].strip.split(",")
        

    df.Date = pd.to_datetime(df.Date)
    if edit_type == "Add":
        # Add colelctable to dataframe
        new_row = pd.DataFrame({
            k: [dt.datetime.strptime(v, "%d-%m-%Y")] if k == "Date" else [v]
            for k, v in input_values.items()})
        
        edited_df = pd.concat([df, new_row], ignore_index=True)
        edited_df = edited_df.reset_index(drop=True)
        return edited_df
    
    else:
        # Delete collectable
        input_values["Date"] = dt.datetime.strptime(input_values["Date"], "%d-%m-%Y")
        
        if "BelongsTo" in df.columns:
            edited_df = df.loc[~(
                (df["Collectable"] == input_values["Collectable"]) &
                (df["BelongsTo"] == input_values["BelongsTo"]) &
                (df["Date"] == input_values["Date"]))]
        else:
            edited_df = df.loc[~(
                (df["Band"] == input_values["Band"]) &
                (df["Date"] == input_values["Date"]))]

        st.write(edited_df)
        return edited_df  
