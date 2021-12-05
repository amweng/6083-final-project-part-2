import streamlit as st
import functions
import datetime
import time


def show():
    '### This was just an attempt at getting some kind of chart to render.'
    '### Also to get multiple pages up and running!'

    local_date_time = datetime.datetime.now()
    local_time = local_date_time.time()

    time_str = functions.time_to_time_with_tz(local_time)
    st.write(time_str)

    query = "SELECT * FROM resources ORDER BY specification;"
    df = functions.query_db(query)
    st.table(df)
