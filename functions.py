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
        new_entries = input_values["Band"].strip().split(",")
    except:
        new_entries = input_values["Collectable"].strip().split(",")
        
    df.Date = pd.to_datetime(df.Date, format="%d-%m-%Y", errors='coerce')
    edited_df = df.copy()
    
    if edit_type == "Add":
        # Add to dataframe
        for i, entry in enumerate(new_entries):
            input_values["Band"] = entry.strip()
            if i == 0:
                input_values["Headliner"] = 1
            else:
                input_values["Headliner"] = 0
            
            new_row = pd.DataFrame({
                k: [dt.datetime.strptime(v, "%d-%m-%Y")] if k == "Date" else [v]
                for k, v in input_values.items()})
            
            edited_df = pd.concat([edited_df, new_row], ignore_index=True)
            edited_df = edited_df.reset_index(drop=True)
        return edited_df
    
    else:
        # Delete from dataframe
        input_values["Date"] = dt.datetime.strptime(input_values["Date"], "%d-%m-%Y")
        
        if "BelongsTo" in edited_df.columns:
            edited_df = edited_df.loc[~(
                (edited_df["Collectable"] == input_values["Collectable"]) &
                (edited_df["BelongsTo"] == input_values["BelongsTo"]) &
                (edited_df["Date"] == input_values["Date"]))]
        else:
            edited_df = df.loc[~(
                (edited_df["Band"] == input_values["Band"]) &
                (edited_df["Date"] == input_values["Date"]))]

        return edited_df  
