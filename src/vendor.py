import pandas as pd
import streamlit as st
import functions
import datetime
import time


def show():
    '### This was just an attempt at getting some kind of chart to render.'
    '### Also to get multiple pages up and running!'

    aVendorType = ["Entertainment", "Caterers", "Venues"]
    vendor_type = st.sidebar.selectbox("Which vendor type applies to you?", aVendorType)




    if (vendor_type == "Entertainment"):

        q_vendors = "SELECT resourceType, typeid, name FROM resources_" + vendor_type + ";"
        df_vendors = functions.query_db(q_vendors)

        st.table(df_vendors)

        a_vendor_names = df_vendors['name'].tolist()

        a_vendor_ids = df_vendors['typeid'].tolist()

        vendor_name = st.sidebar.selectbox("Select act name", a_vendor_names)
        resource_type = vendor_type
        type_id = a_vendor_ids[a_vendor_names.index(vendor_name)]


        st.write('my resource id: ' + resource_type + " " + str(type_id))
        st.write('### My requirements')
        st.write('### Add requirement')

    if (vendor_type == "Caterers"):
        q_vendors = "SELECT resourceType, typeid, name FROM resources_" + vendor_type + ";"
        df_vendors = functions.query_db(q_vendors)

        st.table(df_vendors)

        a_vendor_names = df_vendors['name'].tolist()

        a_vendor_ids = df_vendors['typeid'].tolist()

        vendor_name = st.sidebar.selectbox("Who are you?", a_vendor_names)
        resource_type = vendor_type
        type_id = a_vendor_ids[a_vendor_names.index(vendor_name)]

        st.write('### My requirements')
        st.write('### Add requirement')
        st.write('### My menus')

    if (vendor_type == "Venues"):

        q_vendors = "SELECT resourceType, typeid, name, address FROM resources_" + vendor_type + ";"
        df_vendors = functions.query_db(q_vendors)

        st.table(df_vendors)

        a_vendor_names = df_vendors['name'].tolist()

        a_vendor_ids = df_vendors['typeid'].tolist()

        vendor_name = st.sidebar.selectbox("Who are you?", a_vendor_names)
        resource_type = vendor_type
        type_id = a_vendor_ids[a_vendor_names.index(vendor_name)]

        st.write('### My requirements')
        st.write('### Add requirement')
        st.write('### My menus')








    ts = pd.Timestamp.now()
    st.write(ts)
    st.write(type(ts))

    time_str = functions.pd_timestamp_to_dt_with_tz(ts)
    st.write(time_str)

    query = "SELECT * FROM events ORDER BY eventID;"
    df = functions.query_db(query)
    st.table(df)
