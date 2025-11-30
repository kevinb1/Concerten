import pandas as pd
import numpy as np
from io import BytesIO
import streamlit as st
import datetime as dt
from streamlit_gsheets import GSheetsConnection


def update_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def return_table(conn, table_name):
    """Returns a table, given a connector and a table name

    Args:
        conn (_type_): Connection to the data source
        table_name (str): Name of table

    Returns:
        DataFrame: Dataframe of the table
    """
    df = conn.read(worksheet=table_name)
    return df

def return_id_from_dim(conn, table_name, column, values):
    if "dim" not in table_name:
        raise ValueError("Table name must be a dimension table (dim...)")
    
    if not isinstance(values, list):
        values = [values]
        
    
    df = return_table(conn, table_name)
    matched_value = df[df[column].isin(values)] \
                    .drop(columns=[column]) \
                    .select_dtypes(include=np.number) \
                    .values.flatten().tolist()
    
    return matched_value

def del_from_GSheet(conn, table_name, rows):
    old_df = return_table(conn, table_name)
    
    new_df = old_df.drop(index=rows.index).reset_index(drop=True)
    
    conn.update(data=new_df, worksheet=table_name)

def add_to_GSheet(conn, table_name, new_row, to_check):
    old_df = return_table(conn, table_name)
    
    # explode the band column
    new_rows = new_row.explode("BandID").reset_index(drop=True)
    
    # Price and headliner are only applied to headliner
    new_rows.Price = new_rows.apply(lambda x: x.Price if x.Headliner == x.BandID else 0, axis=1)
    new_rows.Headliner = new_rows.apply(lambda x: 1 if x.Headliner == x.BandID else 0, axis=1)
    
    return new_rows



def querried_df(df, **kwargs):
    """
    Filter a pandas DataFrame using flexible keyword arguments

    Args:
        df (DataFrame): The DataFrame to filter.
        **kwargs: Column-based filtering rules. Each key must be a column name.
            The value determines how filtering is applied:
                - Exact match: Colname="value"
                - Multiple options: Colname=["value1", "value2"]
                - Callable: Colname=lambda x: x > 1000

    Returns:
        DataFrame: A filtered DataFrame containing only the rows that satisfy all provided filtering conditions.
    """
    
    # If no filters provided, return original df
    if not kwargs:
        return df
    
    # Create mask variable
    mask = pd.Series(True, index=df.index)
    # Loop over kwargs to build mask
    for col, val in kwargs.items():
            # Skip filtering if value is None
            if val is None:
                continue
            
            # Check for (lambda) function
            if callable(val):
                cond = val(df[col])
            # Check for list, tuple or set
            elif isinstance(val, (list, tuple, set)):
                cond = df[col].isin(val)
            # Single value filter
            else:
                cond = df[col] == val

            # ensure cond is a boolean Series
            if not isinstance(cond, pd.Series):
                # this could happen if callable returned a plain bool; coerce
                cond = pd.Series(bool(cond), index=df.index)

            mask &= cond

    return df[mask]

def new_id(ids):
    """
    Generate a new unique ID (int) based on existing IDs

    Args:
        ids (iterable): iterable object containing existing IDs

    Returns:
        int: new integer id number
    """
    # Generate initial ID
    initial_id = max(ids) + 1
    
    # Ensure ID is unique
    while initial_id in ids:
        # Increment ID
        initial_id += 1

    return initial_id
