import streamlit as st
import functions


def show():
    # This page surveys the aims of the project, gives a few high-level statistics on the data
    # and suggests how the user can interact with the applicaiton.
    st.write(
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
    )
    all_tables = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';"
    all_table_names = functions.query_db(all_tables)["relname"].tolist()

    st.write('# List of all relation names:')

    st.write(all_table_names)

    ' ## todo: figure out how to compute some basic counting statistics over number of entries and display these as graphs / charts, etc.'

