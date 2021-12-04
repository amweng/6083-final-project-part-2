import streamlit as st
import functions
from enum import Enum

user = 0
action = 0
    

def UI_selectAction():
    aEventPlannerActions = ["Make a New Event", "View Your Events", "Book Resources", "Cancel an Event"]
    page = st.sidebar.selectbox("What do you want to do?", aEventPlannerActions)

def UI_Display():
    UI_selectEP

def makeEvent():
    pass


def show():
    qEventPlanners = "SELECT first_name, last_name FROM event_planners;"
    dfEventPlannerNames = functions.query_db(qEventPlanners)
    dfEventPlannerNames['name'] = (dfEventPlannerNames['first_name'] + ' ' + dfEventPlannerNames['last_name'])
    aEventPlannerNames = dfEventPlannerNames['name'].tolist()
    user = st.sidebar.selectbox("Who are you?", aEventPlannerNames)

    st.write(user)
    
