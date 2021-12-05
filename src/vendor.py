import pandas as pd
import streamlit as st
import functions
import datetime
import time


def show():
    '### This was just an attempt at getting some kind of chart to render.'
    '### Also to get multiple pages up and running!'

    ts = pd.Timestamp.now()
    st.write(ts)
    st.write(type(ts))

    time_str = functions.pd_timestamp_to_dt_with_tz(ts)
    st.write(time_str)

    query = "SELECT * FROM events ORDER BY eventID;"
    df = functions.query_db(query)
    st.table(df)
