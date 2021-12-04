import streamlit as st
import psycopg2
from configparser import ConfigParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Function Definitions
@st.cache
def get_config(filename="database.ini",
               section="postgres"):
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

    print(parser.items('postgres'))

    return {k: v for k, v in parser.items(section)}


@st.cache(allow_output_mutation = True)
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