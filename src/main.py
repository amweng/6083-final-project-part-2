import streamlit as st
import psycopg2
from configparser import ConfigParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function Definitions
@st.cache
def get_config(filename="database.ini", section="postgres"):
    # Establishes the connection with the database based on the parameters
    # within the database.ini file.  You should update these parameters such
    # that they are as follows:
    #
    # database.ini
    # 1 [postgres]
    # 2 host=localhost
    # 3 port=5432
    # 4 dbname=NETID_db
    # 5 user=NETID
    # 
    # note, if editing on jedi.poly.edu, this can be done by navigating to the folder
    # containing the database.ini file and executing 'nano database.ini' to pull up the
    # in-terminal nano text editor.  Write using ctl-O and exit with ctl-X.
    
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

@st.cache
def query_db(sql: str):
    # Function is taken from the in-class demo on launching a streamlit
    # application.  Takes in an SQL command in the form of a string and
    # returns a pandas dataframe containing the data returned by the 
    # database.

    # print(f"Running query_db(): {sql}")

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Obtain data
    data = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df

# Page Contents
page = st.sidebar.selectbox("Navigation panel:", ["Welcome", "Raw Data"])

if page == "Welcome":
    # This page surveys the aims of the project, gives a few high-level statistics on the data
    # and suggests how the user can interact with the applicaiton.
    '''
    # Database-Driven Event Planning
    by Andrew Weng (aw4108) & Russell Wustenberg (rw2873)

    Submitted in fulfillment of CS-GY 6083, Principles of Database Systems (Fall 2021),

    taught by Professor Julia Stoyonovitch, NYU Tandon School of Engineering.

    ---
    This application was developped by Andrew Weng (aw4108) and Russell Wustenberg (rw2873) as the final project
    for CS-GY 6083, Principles of Database Systems, taught by Julia Stoyonovitch at NYU's Tandon School of Engineering.
    The application is built on top of a Postgres SQL database that comes pre-populated with synthetic data crafted
    for this application.  
    
    ## The Goal
    The goal of this application is to emulate an event planning service.  Event planning is notoriously difficult
    due to the complexity of coordination between the venue, the guests, and any resources the event may need.  Our
    service helps streamline the event planning process by making convenient the reservation of resources and communication
    between the event planner, the guests and any third-party vendors.
    '''
    all_tables = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';"
    all_table_names = query_db(all_tables)["relname"].tolist()
    
    '# List of all relation names:'
    st.write(all_table_names)

    ' ## todo: figure out how to compute some basic counting statistics over number of entries and display these as graphs / charts, etc.'
    
elif page == "Raw Data":

    '### This was just an attempt at getting some kind of chart to render.'
    '### Also to get multiple pages up and running!'

    query = "SELECT fee FROM resources ORDER BY fee;"
    df = query_db(query)
    st.bar_chart(df)