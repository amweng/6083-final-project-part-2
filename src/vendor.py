import streamlit as st
import functions


def show():
    '### This was just an attempt at getting some kind of chart to render.'
    '### Also to get multiple pages up and running!'

    query = "SELECT fee FROM resources ORDER BY fee;"
    df = functions.query_db(query)
    st.bar_chart(df)
