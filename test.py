import pandas as pd
import numpy as np
import streamlit as st

def sidebar_filter(header_name, *cols2filter):
    for filter_obj in cols2filter:
        if len(filter_obj) != 2:
            raise ValueError(f"Each tuple must have length 2, got {len(filter_obj)}: {filter_obj}")
    
sidebar_filter("Filters", ("x", "x"), ("x", "x"), ("x", "x"))