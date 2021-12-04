import streamlit as st
import functions

def show():

    st.write('### This was just an attempt at getting some kind of chart to render.'
    'Also to get multiple pages up and running!')

    option = st.selectbox('What would you like to know about entertainment?', ('fee', 'genre', 'contentRating'))
    st.write('You selected:', option)
    query = "SELECT " + option + ", name FROM resources_entertainment ORDER BY " + option + ";"
    df = functions.query_db(query)
    st.table(df)